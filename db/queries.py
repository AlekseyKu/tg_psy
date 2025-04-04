import aiosqlite
from datetime import datetime

DB_PATH = "skazka.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                subscription TEXT DEFAULT 'free',
                subscription_end TEXT,
                coins INTEGER DEFAULT 0,
                daily_limit INTEGER DEFAULT 1,
                audio_limit INTEGER DEFAULT 3
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT,
                audio_path TEXT,
                type TEXT,
                date TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                user_id INTEGER PRIMARY KEY,
                tts_minutes REAL DEFAULT 0,
                tales_count INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS skazki (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                audio_path TEXT,
                type TEXT
            )
        """)
        await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()


async def add_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, subscription, subscription_end, coins, daily_limit, audio_limit) "
            "VALUES (?, 'free', ?, 0, 1, 3)",
            (user_id, datetime.now().isoformat())
        )
        await db.commit()


async def update_user(user_id, subscription=None, coins=None, daily_limit=None, audio_limit=None):
    async with aiosqlite.connect(DB_PATH) as db:
        fields = []
        values = []
        if subscription:
            fields.append("subscription = ?")
            values.append(subscription)
        if coins is not None:
            fields.append("coins = ?")
            values.append(coins)
        if daily_limit is not None:
            fields.append("daily_limit = ?")
            values.append(daily_limit)
        if audio_limit is not None:
            fields.append("audio_limit = ?")
            values.append(audio_limit)
        if fields:
            values.append(user_id)
            await db.execute(f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?", values)
            await db.commit()


async def save_tale(user_id, text, audio_path, tale_type):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO tales (user_id, text, audio_path, type, date) VALUES (?, ?, ?, ?, ?)",
            (user_id, text, audio_path, tale_type, datetime.now().isoformat())
        )
        await db.commit()


async def get_user_tales(user_id, limit=30):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT text, audio_path, type, date FROM tales WHERE user_id = ? ORDER BY date DESC LIMIT ?",
            (user_id, limit)
        ) as cursor:
            return await cursor.fetchall()


async def update_stats(user_id, tts_minutes=0, tales_count=1):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO stats (user_id, tts_minutes, tales_count) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET tts_minutes = tts_minutes + ?, tales_count = tales_count + ?",
            (user_id, tts_minutes, tales_count, tts_minutes, tales_count)
        )
        await db.commit()


async def get_stats(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT tts_minutes, tales_count FROM stats WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()


async def get_random_skazka(tale_type="text"):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT text, audio_path FROM skazki WHERE type = ? ORDER BY RANDOM() LIMIT 1",
            (tale_type,)
        ) as cursor:
            return await cursor.fetchone()


async def add_skazka(text, audio_path, tale_type):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO skazki (text, audio_path, type) VALUES (?, ?, ?)",
            (text, audio_path, tale_type)
        )
        await db.commit()
