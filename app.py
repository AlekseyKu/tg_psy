import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from openai import OpenAI

# Загрузка переменных из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токены и константы
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
XAI_API_KEY = os.getenv("AI_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
TRAINING_DATA_FILE = "training_data.json"

# Отладочный вывод
print(f"Loaded BOT_TOKEN: {TELEGRAM_TOKEN}")
print(f"Loaded AI_TOKEN: {XAI_API_KEY}")
print(f"Loaded ADMIN_ID: {ADMIN_ID}")

if not TELEGRAM_TOKEN or not XAI_API_KEY:
    raise ValueError("Токены не загружены из .env. Проверьте файл .env")

# Инициализация бота
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Инициализация клиента xAI
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)


# Состояния для обучения
class TrainingStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()


# Состояние для отслеживания количества сообщений
class DialogState(StatesGroup):
    message_count = State()


# Функции для работы с данными
def load_training_data():
    try:
        with open(TRAINING_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_training_data(data):
    with open(TRAINING_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Запрос к Grok API через OpenAI клиент
def get_grok_response(message, message_count):
    training_data = load_training_data()
    context = "\n".join([f"Вопрос: {d['question']} Ответ: {d['answer']}" for d in training_data])
    system_prompt = (
            "Тебя зовут Ei (Эй), полное имя Empathy AI. "
            "Ты профессиональный психолог с 20-летним опытом, а также близкий друг, который искренне заботится о человеке. "
            "Ты владеешь всеми передовыми и проверенными временем подходами психологии: "
            "когнитивно-поведенческой терапией (КПТ) для переосмысления негативных мыслей, "
            "диалектической поведенческой терапией (ДПТ) для управления эмоциями, mindfulness (осознанностью) "
            "для успокоения, эмоционально-фокусированной терапией (ЭФТ) для работы с чувствами, гештальт-терапией "
            "для осознания текущего момента, психодинамическим подходом для понимания глубинных причин, и позитивной "
            "психологией для акцента на сильных сторонах и надежде. "
            "Твоя цель — общение с людьми как друг и психолог. Выявление проблемы, анализируя ответы пользователя, а также поффессиональная помощь"
            " человеку в кризисной ситуации, создавая доверительную атмосферу. Не пытайся сразу нападать на пользователя вопросами 'что тебя беспокоит' и т.п. Анализируй ответы пользователя"
            "Отвечай кратко (2-4 предложения), но профессионально: сразу прояви эмпатию, при необходимости предложи конкретное действие, "
            "основанное на одной из психологических техник, которое поможет прямо сейчас. "
            "Всегда завершай свои мысли, чтобы ответ был законченным по смыслу: не обрывай предложения. Не повторяй вопрос "
            "пользователя в ответе и избегай общих фраз вроде 'я понимаю, как тебе тяжело' — вместо этого покажи понимание "
            "через конкретные действия. Предлагай необходимые техники только в случае, когда это необходимо."
            "Отвечай на русском языке, используй теплый, искренний и дружеский тон, как будто ты близкий друг с "
            "профессиональными знаниями. Если ситуация кризисная и это третье или последующее сообщение в диалоге, "
            "и если это уместно относительно диалога, можешь добавить в самом конце ответа (и только один раз) "
            "предложение: 'Ты всегда можешь связаться с нашими онлайн-психологами, нажав в меню \"Психолог-онлайн\".' "
            "Старайся заверщать ответ конкретным действием или вопросом, чтобы пользователь мог сразу что-то предпринять "
            "или продолжить диалог. "
            "Вот примеры предыдущих диалогов:\n" + context
    )
    try:
        completion = client.chat.completions.create(
            model="grok-2-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Сообщение номер {message_count}: {message}"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        response = completion.choices[0].message.content.strip()
        logging.info(f"Ответ API: {response}")
        return response
    except Exception as e:
        logging.error(f"Ошибка API: {e}")
        raise


# Команда /start
@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    # Сбрасываем счетчик сообщений при команде /start
    await state.update_data(message_count=0)
    await message.answer(
        "Привет! Я твой друг и психолог, здесь, чтобы помочь. "
        "Расскажи, что тебя волнует."
    )


# Команда /train
@dp.message(Command("train"))
async def train_command(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Напиши вопрос для обучения:")
        await state.set_state(TrainingStates.waiting_for_question)
    else:
        await message.answer("У тебя нет доступа к обучению.")


# Сбор вопроса
@dp.message(TrainingStates.waiting_for_question)
async def process_question(message: types.Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("Теперь напиши ответ:")
    await state.set_state(TrainingStates.waiting_for_answer)


# Сбор ответа и сохранение
@dp.message(TrainingStates.waiting_for_answer)
async def process_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    question = data["question"]
    answer = message.text
    training_data = load_training_data()
    training_data.append({"question": question, "answer": answer})
    save_training_data(training_data)
    await message.answer("Данные сохранены!")
    await state.clear()


# Обработка всех сообщений
@dp.message()
async def handle_message(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        try:
            # Получаем текущее состояние (количество сообщений)
            data = await state.get_data()
            message_count = data.get("message_count", 0)

            # Увеличиваем счетчик сообщений
            message_count += 1
            await state.update_data(message_count=message_count)

            # Передаем message_count в get_grok_response
            response = get_grok_response(message.text, message_count)
            await message.answer(response)
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            await message.answer("Извини, что-то пошло не так. Попробуй еще раз!")


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())