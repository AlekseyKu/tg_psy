# Пока models.py можно оставить пустым или зарезервировать для ORM-схем (например, pydantic или dataclass).
# Это пригодится, если в будущем ты захочешь перейти на PostgreSQL, Tortoise ORM, SQLAlchemy и т.д.

# Пример структуры (заглушка):

from dataclasses import dataclass

@dataclass
class User:
    user_id: int
    subscription: str
    subscription_end: str
    coins: int
    daily_limit: int
    audio_limit: int
