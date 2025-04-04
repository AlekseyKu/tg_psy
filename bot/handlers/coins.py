from aiogram import types
from db import queries as db


async def show_coins(message: types.Message):
    user = await db.get_user(message.from_user.id)
    coins = user[3]
    await message.answer(
        f"🪙 Ваш баланс: {coins} монет\n\n"
        "📖 Сказка по теме — 1 монета\n"
        "🎧 Аудиосказка — 1 монета\n"
        "🧸 Именная сказка — 2 монеты\n"
        "🌙 Сказка с колыбельной — 2 монеты\n\n"
        "Пакеты:\n5 монет — 149 ₽\n15 монет — 399 ₽\n50 монет — 999 ₽\n"
        "Покупка скоро будет доступна!"
    )