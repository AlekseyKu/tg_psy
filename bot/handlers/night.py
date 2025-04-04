from aiogram import types
from db import queries as db
from core.ai import get_fairytale
from core.tts import synthesize_voice_with_yandex
from aiogram.types import FSInputFile
import os
from datetime import datetime


async def night_tale(message: types.Message):
    user = await db.get_user(message.from_user.id)
    subscription, coins = user[1], user[3]

    if subscription not in ["extended", "premium"]:
        await message.answer("🛌 Сказка на ночь доступна только для Расширенного и Премиум тарифов!")
        return

    theme = "успокаивающая сказка перед сном для ребёнка"
    message_count = int(datetime.now().timestamp()) % 100000  # для уникальности вызова

    fairytale = get_fairytale(theme, message_count)
    voice = "jane"  # Можно кастомизировать позже

    audio_path = synthesize_voice_with_yandex(fairytale, voice)
    if audio_path:
        await db.save_tale(message.from_user.id, fairytale, audio_path, "night_audio")
        await db.add_skazka(fairytale, audio_path, "night_audio")
        await message.answer("🌙 Включаю ночную колыбельную сказку...")
        await message.answer_voice(FSInputFile(audio_path), caption="Сладких снов... 💤")
    else:
        await db.save_tale(message.from_user.id, fairytale, None, "night")
        await db.add_skazka(fairytale, None, "night")
        await message.answer(fairytale + "\n\n(Ошибка озвучки — читаю текстом)")
