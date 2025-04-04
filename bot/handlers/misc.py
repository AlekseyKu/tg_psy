from aiogram import types


async def choose_voice(message: types.Message):
    await message.answer("Доступные голоса:\n🐾 Кот Баюна (ermil)\n🧜‍♀️ Русалка (jane)\n\nВыбор голоса пока в разработке!")


async def show_help(message: types.Message):
    await message.answer(
        "ℹ Я помогу вам погрузиться в мир сказок!\n"
        "Используйте кнопки меню или команды:\n"
        "/skazka — получить сказку\n"
        "/subscribe — узнать о подписке\n"
        "/coins — проверить монеты"
    )


async def fallback_handler(message: types.Message):
    await message.answer("Я понимаю только команды и кнопки из меню. Попробуйте /start или выберите действие!")
