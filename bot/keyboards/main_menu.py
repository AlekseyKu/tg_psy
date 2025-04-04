from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📖 Расскажи сказку"), KeyboardButton(text="🗣 Выбрать голос")],
        [KeyboardButton(text="📚 Расскажи рандомную сказку"), KeyboardButton(text="🧸 Расскажи именную сказку")],
        [KeyboardButton(text="💫 Подписка"), KeyboardButton(text="🪙 Монеты")],
        [KeyboardButton(text="🛌 Сказка на ночь"), KeyboardButton(text="🎁 Моя коллекция")],
        [KeyboardButton(text="ℹ Помощь")],
    ],
    resize_keyboard=True
)
