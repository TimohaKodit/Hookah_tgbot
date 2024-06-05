from aiogram.fsm.state import StatesGroup, State


class Hookah(StatesGroup):
    strength = State()
    other_taste = State()
    taste_hookah = State()
    time_order = State()
    hookah_bowl = State()
    

class Newsletter(StatesGroup):
    text_newsletter = State()
    news_photo = State()

class Request(StatesGroup):
    phone_number_user = State()

class Request_Master(StatesGroup):
    phone_info = State()
    phone_balance = State()
    change_balance = State()
    id = State()