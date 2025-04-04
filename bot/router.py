# bot/router.py
from aiogram import Dispatcher, F
from bot.handlers import tale, named_tale, subscription, coins, collection, misc, night
from bot.states import DialogState


def setup_routers(dp: Dispatcher):
    # Основные хендлеры
    dp.message.register(tale.start_command, F.text == "/start")
    dp.message.register(tale.tell_tale, F.text == "📖 Расскажи сказку")
    dp.message.register(tale.process_theme, DialogState.awaiting_theme)
    dp.message.register(tale.tell_random_tale, F.text == "📚 Расскажи рандомную сказку")

    # Именная сказка
    dp.message.register(named_tale.tell_named_tale, F.text == "🧸 Расскажи именную сказку")
    dp.message.register(named_tale.process_named_tale, F.state == DialogState.awaiting_name)

    # Подписка и монеты
    dp.message.register(subscription.subscription_info, F.text == "💫 Подписка")
    dp.message.register(coins.show_coins, F.text == "🪙 Монеты")

    # Коллекция и ночь
    dp.message.register(collection.show_collection, F.text == "🎁 Моя коллекция")
    dp.message.register(night.night_tale, F.text == "🛌 Сказка на ночь")

    # Прочее
    dp.message.register(misc.choose_voice, F.text == "🗣 Выбрать голос")
    dp.message.register(misc.show_help, F.text == "ℹ Помощь")

    # Fallback должен быть последним
    dp.message.register(misc.fallback_handler)
