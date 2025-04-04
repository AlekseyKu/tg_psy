# bot/handlers/tale.py
import logging

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from bot.states import DialogState
from core.ai import get_fairytale
from core.tts import synthesize_voice_with_yandex
from db import queries as db
from aiogram.types import FSInputFile
from bot.keyboards.main_menu import main_menu
import os
from datetime import datetime


async def start_command(message: types.Message, state: FSMContext):
    await db.add_user(message.from_user.id)
    await state.clear()
    await state.update_data(message_count=0)
    await message.answer(
        "✨ Добро пожаловать в “Портал в Сказку”!\n"
        "Я расскажу волшебные сказки голосами Кота Баюна и Русалки.\n"
        "Выбирайте — и откроем портал…",
        reply_markup=main_menu
    )


async def tell_tale(message: types.Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if not user:
        await db.add_user(message.from_user.id)
        user = await db.get_user(message.from_user.id)

    if user[1] == "free":
        await message.answer("Эта функция доступна только для подписчиков. Оформите подписку — /subscribe")
    else:
        await state.set_state(DialogState.awaiting_theme)
        await state.update_data(message_count=0)
        await message.answer("🎯 Задай тему для сказки:")


async def process_theme(message: types.Message, state: FSMContext):
    # logging.warning(f"[FSM] handler triggered. CURRENT STATE: {await state.get_state()}")

    user = await db.get_user(message.from_user.id)
    subscription, coins = user[1], user[3]
    voice = "jane"

    data = await state.get_data()
    message_count = data.get("message_count", 0) + 1
    await state.update_data(message_count=message_count)

    fairytale = get_fairytale(message.text, message_count)
    await db.save_tale(message.from_user.id, fairytale, None, "text")
    await db.add_skazka(fairytale, None, "text")

    if subscription == "premium" or coins > 0:
        audio_path = synthesize_voice_with_yandex(fairytale, voice)
        if audio_path:
            await db.save_tale(message.from_user.id, fairytale, audio_path, "audio")
            await db.add_skazka(fairytale, audio_path, "audio")
            await message.answer_voice(FSInputFile(audio_path), caption="Вот твоя сказка 🎙")
            if subscription != "premium":
                await db.update_user(message.from_user.id, coins=coins - 1)
        else:
            await message.answer(fairytale + "\n\nОшибка озвучки 😢")
    else:
        await message.answer(fairytale + "\n\n🪙 У вас не хватает монет для аудио. Купите — /coins")

    await state.clear()


async def tell_random_tale(message: types.Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if not user:
        await db.add_user(message.from_user.id)
        user = await db.get_user(message.from_user.id)

    subscription, coins, daily_limit, audio_limit = user[1], user[3], user[4], user[5]
    today = datetime.now().date()
    sub_start = datetime.fromisoformat(user[2]).date()

    if subscription == "free":
        if (today - sub_start).days < 3 and audio_limit > 0:
            skazka = await db.get_random_skazka("audio")
            if skazka and skazka[1] and os.path.exists(skazka[1]):
                await db.update_user(message.from_user.id, audio_limit=audio_limit - 1)
                await db.save_tale(message.from_user.id, skazka[0], skazka[1], "audio")
                await message.answer_voice(FSInputFile(skazka[1]), caption="Вот твоя случайная сказка 🎙")
            else:
                await message.answer("Ошибка: нет доступных аудиосказок или файл отсутствует!")
        else:
            skazka = await db.get_random_skazka("text")
            if skazka:
                await db.save_tale(message.from_user.id, skazka[0], None, "text")
                await message.answer(skazka[0] + "\n\n🧙 Голос Баюна уснул…\n"
                                                     "Но вы можете снова услышать его, оформив Золотую подписку — /subscribe")
            else:
                await message.answer("Ошибка: нет доступных текстовых сказок!")
    else:
        skazka = await db.get_random_skazka("audio") if coins > 0 or subscription == "premium" else await db.get_random_skazka("text")
        if skazka:
            if skazka[1] and os.path.exists(skazka[1]):
                await db.save_tale(message.from_user.id, skazka[0], skazka[1], "audio")
                await message.answer_voice(FSInputFile(skazka[1]), caption="Вот твоя случайная сказка 🎙")
                if subscription != "premium":
                    await db.update_user(message.from_user.id, coins=coins - 1)
            else:
                await db.save_tale(message.from_user.id, skazka[0], None, "text")
                await message.answer(skazka[0])
        else:
            await message.answer("Ошибка: нет доступных сказок в базе!")
