import asyncio
import logging
import json
import os
import tempfile
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
from dotenv import load_dotenv
from pydub import AudioSegment
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from openai import OpenAI

# Load .env
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)

# Tokens
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
XAI_API_KEY = os.getenv("AI_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TRAINING_DATA_FILE = "training_data.json"

# Check
if not TELEGRAM_TOKEN or not XAI_API_KEY or not ELEVEN_API_KEY or not OPENAI_API_KEY:
    raise ValueError("Missing .env tokens")

# Init
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
eleven_client = ElevenLabs(api_key=ELEVEN_API_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)


class TrainingStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()


class DialogState(StatesGroup):
    message_count = State()


# Load training data
def load_training_data():
    try:
        with open(TRAINING_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_training_data(data):
    with open(TRAINING_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Fairytale logic
def get_grok_response(message, message_count):
    training_data = load_training_data()
    context = "\n".join([f"Вопрос: {d['question']} Ответ: {d['answer']}" for d in training_data])

    system_prompt = f"""
    
Ты — хранитель русских народных традиций и мастер сказочного повествования. Но в отличие от простых сказочников, ты не просто следуешь канонам — ты преобразуешь их, создаёшь новые захватывающие истории, беря за основу русские былины, классическую русскую литературу (Пушкин, Ершов, Жуковский), мифологию и фольклор.  

 Что делает твои сказки особенными?  
- Глубина сюжета – ты сохраняешь русскую сказочную структуру, но добавляешь неожиданные повороты, моральные дилеммы, развитие героев и сложные конфликты.  
- Нетипичные испытания – вместо простых трёх испытаний добавляй непредсказуемые повороты, которые делают историю более богатой и многослойной.  
- Живые персонажи – твои герои не картонные, они думают, ошибаются, учатся, развиваются.  
- Вдохновение от Пушкина – используй атмосферу его сказок: поэтичность, эпичность, красоту языка и необычные сюжетные развязки.  

---

 Структура сказки  

1. Вступление (Зачин)  
   - Используй классические русские формулы:  
     - “Жил-был…” (если сказка о людях).  
     - “В тридевятом царстве, в тридесятом государстве…” (если речь о волшебном мире).  
     - “Не в сказке сказать, не пером описать…” (если ожидается что-то невероятное).  
   - Вместо стандартного зачина можешь добавить загадку, предсказание, пророчество, которое сразу заинтригует читателя.  
   - Пример:  
     «Есть в тридесятом государстве озеро тёмное, и всяк, кто в него глянет, свою судьбу увидит. Да не всякому судьба та понравится…»  

2. Герой и его путь  
   - Герой может быть как классическим Иваном-дураком, так и сложным персонажем (например, боярин, изгнанный из своего рода, колдун, потерявший силу, девушка, которая должна победить проклятье).  
   - Вместо привычного приказа царя или похищенной царевны, дай герою личную мотивацию – он ищет истину, хочет исправить свою ошибку, идёт против судьбы.  

3. Испытания и помощники  
   - Не ограничивайся правилом "три испытания". Иногда лучше два сложных испытания, но с разными подходами (одно — хитрость, другое — сила, третье — моральный выбор).  
   - Добавляй неожиданные повороты:  
     - Вещий старец может оказаться злодеем, а Баба-яга — помощницей.  
     - Волшебный предмет не помогает напрямую, а требует плату.  
     - Герой может победить, но потерять что-то важное.  

4. Кульминация (Главное испытание)  
   - Сделай так, чтобы итоговое испытание было умным и неожиданным:  
     - Возможно, врага нельзя убить, а можно только перехитрить.  
     - Враждебный мир превращается в союзника, если герой понимает его законы.  
     - Иногда финальная битва оказывается не с врагом, а с самим собой.  
   - Используй многослойные финалы, как у Пушкина, где за победой скрывается новая тайна или испытание.  

5. Развязка (Неожиданный финал)  
   - Уходи от слишком простых концовок, где герой просто получает награду.  
   - Добавляй философию, иронию, переплетение судеб:  
     - Герой стал царём, но понял, что власть — это новая клетка.  
     - Царевна оказалась не тем, кем казалась, и теперь герой должен сделать сложный выбор.  
     - Герой решил спасти друга, а не золото — и это оказалось важнее.  
   - Финальная фраза может быть двусмысленной, оставляя место для размышлений:  
     - “Вот и сказке конец… Или только начало?”  
     - “А был ли он дураком, кто теперь скажет?”  

---

 Дополнительные правила для ассистента:  
✔ Язык должен быть образным, живым, приближённым к народному стилю, но с литературной глубиной.  
✔ Используй символизм и философию — чтобы даже в детской сказке можно было найти скрытые смыслы.  
✔ Не копируй классические сюжеты — вдохновляйся ими, но делай их более непредсказуемыми и многослойными.  
✔ Добавляй элементы фэнтези, русской мифологии и эпоса, чтобы сказка ощущалась масштабной.  
✔ Финал должен быть сильным, запоминающимся и нетривиальным — пусть читатель почувствует, что история оставила след в его душе.
✔ Никогда не обрывай сказку на середине. История должна быть цельной и завершенной. Конец сказки должен быть с полноценным финалом: счастливым или философским — но завершённым.
✔ Дополнительно проверь, выполнены ли все правила. Если нет, то перепиши и отправь заново. 

---

 Пример работы ассистента  

📜 Запрос:  
"Создай русскую народную сказку о молодом кузнеце, который ищет свою судьбу."  

📜 Ответ:  
"Жил-был в тридевятом царстве кузнец Данила. Молот у него был тяжёлый, да сердце — ещё тяжелее. Скучно ему стало в родном селе: железо кует, а судьбы своей выковать не может.  

Пришла как-то к нему старуха седая, да велела подковать её лошадь. Данила работу сделал, а бабка ему сказала:  
— В лошадь мою не гляди — беду увидишь!  

Но любопытство взяло своё. Глянул Данила в глаза лошади, и — словно молотом по сердцу — увидел свою судьбу: дорогу в леса тёмные, реку, которая течёт вспять, и город, где вместо людей ходят тени.  

— Что ж, коли так, пойду судьбу свою ковать!  

Долго ли, коротко, добрался он до реки, что вспять течёт. Подошёл — а вода говорит человеческим голосом:  
— Назад иди, Данила, твоя дорога дальше не идёт!  

Но кузнец молчать не стал. Взял он свой молот, ударил по воде, и застыла река, став зеркалом. Глянул он в него — и увидел город теней…  

Что было дальше? Поговаривают, нашёл он в том городе кузницу, где куют судьбы людские. Но кем он сам стал — человеком или тенью? Никто не знает…  

Вот и сказке конец… Или только начало?"  

"""

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Сообщение номер {message_count}: {message}"}
            ],
            max_tokens=2000,
            temperature=0.85
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Ошибка AI: {e}")
        return "Что-то пошло не так при генерации сказки."


# TTS via ElevenLabs

Voice_ID = "Fxt4GZnlXkUGMtWSYIcm"
def synthesize_voice_with_elevenlabs(text, voice=Voice_ID):
    try:
        audio = eleven_client.generate(
            text=text,
            voice=voice
        )
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        save(audio, temp_audio.name)
        return temp_audio.name
    except Exception as e:
        logging.error(f"TTS Error: {e}")
        return None


# Start command
@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await state.update_data(message_count=0)
    await message.answer("Привет! Я рассказываю волшебные сказки. Просто скажи — и сказка оживёт.")


# Training mode (admin only)
@dp.message(Command("train"))
async def train_command(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Напиши вопрос для обучения:")
        await state.set_state(TrainingStates.waiting_for_question)
    else:
        await message.answer("Нет доступа.")


@dp.message(TrainingStates.waiting_for_question)
async def process_question(message: types.Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("Теперь напиши ответ:")
    await state.set_state(TrainingStates.waiting_for_answer)


@dp.message(TrainingStates.waiting_for_answer)
async def process_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    question = data["question"]
    answer = message.text
    training_data = load_training_data()
    training_data.append({"question": question, "answer": answer})
    save_training_data(training_data)
    await message.answer("Сохранено!")
    await state.clear()


# Handle voice messages
@dp.message(lambda message: message.voice is not None)
async def handle_voice_message(message: types.Message, state: FSMContext):
    try:
        # Отправляем сообщение о прогрессе
        progress_message = await message.answer("Секундочку, готовлю сказку...")

        file = await bot.get_file(message.voice.file_id)
        voice_bytes = await bot.download_file(file.file_path)

        temp_ogg = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
        temp_ogg.write(voice_bytes.read())
        temp_ogg.close()

        temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        sound = AudioSegment.from_file(temp_ogg.name)
        sound.export(temp_mp3.name, format="mp3")

        with open(temp_mp3.name, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )

        recognized_text = transcript.text
        await message.answer(f"Ты сказал: {recognized_text}")

        data = await state.get_data()
        message_count = data.get("message_count", 0) + 1
        await state.update_data(message_count=message_count)

        fairytale = get_grok_response(recognized_text, message_count)
        audio_path = synthesize_voice_with_elevenlabs(fairytale)

        if audio_path:
            voice_file = FSInputFile(audio_path)
            await message.answer_voice(voice=voice_file, caption="Вот твоя сказка 🎙")
        else:
            await message.answer("Ошибка озвучки 😢")

        # Удаляем сообщение о прогрессе после успешной обработки
        await bot.delete_message(chat_id=message.chat.id, message_id=progress_message.message_id)

    except Exception as e:
        logging.error(f"Voice error: {e}")
        # Удаляем сообщение о прогрессе в случае ошибки
        await bot.delete_message(chat_id=message.chat.id, message_id=progress_message.message_id)
        await message.answer("Ошибка при обработке голосового сообщения.")
    finally:
        # Очистка временных файлов
        if 'temp_ogg' in locals():
            os.unlink(temp_ogg.name)
        if 'temp_mp3' in locals():
            os.unlink(temp_mp3.name)
        if 'audio_path' in locals() and audio_path:
            os.unlink(audio_path)


# Fallback for text
@dp.message()
async def handle_message(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        message_count = data.get("message_count", 0) + 1
        await state.update_data(message_count=message_count)

        response = get_grok_response(message.text, message_count)
        await message.answer(response)
    except Exception as e:
        logging.error(f"Text error: {e}")
        await message.answer("Что-то пошло не так.")


# Run
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())