from aiogram import types
from db import queries as db


async def show_collection(message: types.Message):
    user = await db.get_user(message.from_user.id)
    subscription = user[1]

    if subscription in ["extended", "premium"]:
        tales = await db.get_user_tales(message.from_user.id)
        if tales:
            response = "🎁 Ваши последние сказки:\n"
            for tale in tales:
                response += f"{tale[3]} - {tale[2]}\n"
            await message.answer(response)
        else:
            await message.answer("🎁 Пока здесь пусто!")
    else:
        await message.answer("🎁 Коллекция доступна только для Расширенного и Премиум тарифов!")
