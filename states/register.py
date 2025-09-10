from aiogram.fsm.state import State, StatesGroup

class Register(StatesGroup):
    first_name = State()
    last_name = State()
    phone_number = State()
    email = State()
    location = State()
    education = State()
    political_exp = State()
    motivation = State()
    documents = State()
