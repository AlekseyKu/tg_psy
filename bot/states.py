# bot/states.py
from aiogram.fsm.state import State, StatesGroup


class DialogState(StatesGroup):
    awaiting_theme = State()
    awaiting_name = State()
