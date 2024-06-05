from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apps.database.requests import get_strength, get_tastes


#Phone number
phone_number_user = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Поделиться номером телефона', request_contact=True)]
], resize_keyboard=True, one_time_keyboard=True)

#Action
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать кальян')],
    [KeyboardButton(text='Узнать о бонусах')],
    [KeyboardButton(text='Позвать кальянного мастера')]
], resize_keyboard=True)

main_hookah_master = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Посмотреть информацию по 1 пользователю')],
    [KeyboardButton(text='Посмотреть информацию по всем пользователям')],
    [KeyboardButton(text='Изменить баланс бонусов')]
], resize_keyboard=True)

copy_id = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Копировать ID заказа', callback_data='copy_order_id')]
])
bowl_keybord = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Обычная', callback_data='regular_bowl')],
    [InlineKeyboardButton(text='Грейпфрут', callback_data='grapefruit_bowl')]
])

#ADMIN
main_admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Заказать кальян')],
    [KeyboardButton(text='Узнать о бонусах')],
    [KeyboardButton(text='Админ панель')]
], resize_keyboard=True)

admin_pannel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Статистика')],
    [KeyboardButton(text='Сделать рассылку')],
    [KeyboardButton(text='Просмотреть заказы 1 пользователя')],
    [KeyboardButton(text='Назад')]
], resize_keyboard=True)


confirm_orders = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подтвердить заказ', callback_data='confirm')],
    [InlineKeyboardButton(text='Использовать бонусы', callback_data='use_bonuse')]
])


confirm_newsletter = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подтвердить текст', callback_data='confirm_text')],
    [InlineKeyboardButton(text='Добавить фото', callback_data='photo')]
])
confirm = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подтвердить рассылку', callback_data='confirm_newsletter')]
])
bonuses = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Как начисляются бонусы?')], 
    [KeyboardButton(text = 'Назад')]
], resize_keyboard=True) 

use_bon = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='yes')],
    [InlineKeyboardButton(text='Нет', callback_data='no')]
])


async def strength_keyboard():
    strength_kb = InlineKeyboardBuilder()
    strengths = await get_strength()
    
    for strength in strengths:
        strength_kb.add(InlineKeyboardButton(text=strength.name, callback_data=strength.id))
    return strength_kb.adjust(2).as_markup()

async def taste_keyboard():
    taste_kb = InlineKeyboardBuilder()
    tastes = await get_tastes()

    for taste in tastes:
        taste_kb.add(InlineKeyboardButton(text=taste.name, callback_data=taste.id))
    return taste_kb.adjust(2).as_markup()




