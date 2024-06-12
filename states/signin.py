from aiogram.dispatcher.filters.state import StatesGroup, State


class SignIn(StatesGroup):
    phone = State()
    secret_code = State()