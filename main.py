# main.py
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage  # <-- FSM storage
from config import TELEGRAM_TOKEN
from db.queries import init_db
from bot.router import setup_routers



async def main():
    logging.basicConfig(level=logging.INFO)

    # Создаём бота и FSM-хранилище в памяти
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())  # <-- ОБЯЗАТЕЛЬНО для работы FSM

    # Подключаем роутеры
    setup_routers(dp)

    # Инициализация базы
    await init_db()

    # Стартуем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
