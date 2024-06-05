import re
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram import F, Router
from sqlalchemy import select
from apps.keyboards.keyboards import *
from apps.config.config import ADMIN_ID, HOOKAH_MASTER_ID
from aiogram.fsm.context import FSMContext
from apps.states.States import Hookah, Newsletter, Request, Request_Master
from bot_setup import bt
import apps.database.requests as rq
from apps.database.models import Order, User, async_session
from openpyxl import Workbook
from aiogram import types
from aiogram.types import FSInputFile
from sqlalchemy import update

router = Router()







#ADMIN_PANNEL
@router.message(F.text == 'Админ панель')
async def admin_panel(message: Message):
    user_id = message.from_user.id
    if user_id in ADMIN_ID:
        await message.answer('Выберите кнопку, которая вам нужна', reply_markup=admin_pannel)
    else:
        await message.answer('Я тебя не понимаю')

@router.message(F.text == 'Назад')
async def back_to_main_admin(message: Message):
    user_id = message.from_user.id
    if user_id in ADMIN_ID:
        await message.answer('Выберите что вам нужно', reply_markup=main_admin)
    else:
        await message.answer('Я тебя не понимаю')







@router.message(F.text == 'Просмотреть заказы 1 пользователя')
async def orders_one_of_client(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in ADMIN_ID:
        await state.set_state(Request.phone_number_user)
   
        await message.answer('Введите номер телефона пользователя: ')
    else: 
        await message.answer('Я тебя не понимаю')



async def export_order_user_to_excel(phone_number):
    # Получаем все заказы из базы данных для конкретного номера телефона
    async with async_session() as session:
        balance = await session.execute(select(User.bonuce).where(User.phone_number == phone_number))
        res = balance.scalar()
        result = await session.execute(select(Order.phone_number, Order.taste_id, Order.strength_id, Order.time_order, Order.bowl, Order.price, Order.old_bonus, Order.new_bonus).where(Order.phone_number == phone_number))
        orders = result.all()
        
        # Создаем книгу Excel
        wb = Workbook()
        ws = wb.active

        # Добавляем заголовки столбцов
        ws.append(['Телефон', 'Вкус', 'Крепость', 'Время', 'Цена', 'Было бонусов', 'Стало'])
        
        # Добавляем данные о заказах и бонусах
        for order in orders:
           
            
            ws.append([
                order.phone_number,
                order.taste_id,
                order.strength_id,
                order.time_order,  # Преобразование datetime в строку
                order.price, 
                order.old_bonus,
                order.new_bonus  # Добавляем бонусы только для первой строки заказа
            ])
        
        excel_filename = 'order_user.xlsx'
        wb.save(excel_filename)
        return excel_filename





@router.message(Request.phone_number_user)
async def info_user(message: Message, state: FSMContext):
    
    phone_number = message.text
    excel_filename = await export_order_user_to_excel(phone_number)  # Сохраняем данные в Excel
    
    # Отправляем полученный файл
    with open(excel_filename, 'rb') as excel_file:
        await message.answer_document(document=FSInputFile('order_user.xlsx'), caption='Все заказы в Excel файле', reply_markup=main_admin)                         
    await state.clear()     






# NEWSLETTER

@router.message(F.text == 'Сделать рассылку')
async def newsletter(message: Message, state: FSMContext):
    await state.set_state(Newsletter.text_newsletter)
    await message.answer('Введите текст рассылки')


@router.message(Newsletter.text_newsletter)
async def text(message: Message, state: FSMContext):
    await state.update_data(text_newsletter=message.text)
    data = await state.get_data()
    text = data.get('text_newsletter')

    await message.answer(f'Ваш текст:\n{text}', reply_markup=confirm_newsletter)



@router.callback_query(F.data == 'photo')
async def photo(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Отправьте фото')
    await state.set_state(Newsletter.news_photo)

@router.message(Newsletter.news_photo)
async def add_photo(message: Message, state: FSMContext):
    photo_news = message.photo[-1].file_id
    await state.update_data(news_photo=photo_news)

    await message.answer('Подтвердите рассылку', reply_markup=confirm)




@router.callback_query(F.data == 'confirm_newsletter')
async def confirm_and_send_newsletter(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        users = await session.execute(select(User.tg_id))
        users = users.scalars().all()
        data = await state.get_data()
        text = data.get('text_newsletter')
        photo = data.get('news_photo')
        if photo:
            for userx in users:
                await bt.send_photo(userx, photo, caption=text)
        else:
            for userx in users:
                await bt.send_message(userx, text)
        await callback.answer('Рассылка отправлена.')
        await state.clear()


@router.callback_query(F.data == 'confirm_text')
async def confirm_text(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        users = await session.execute(select(User.tg_id))
        users = users.scalars().all()
        data = await state.get_data()
        news_text = data.get('text_newsletter')
        for userx in users:
            await callback.answer()
            await bt.send_message(userx, news_text)
        await state.clear()



async def export_orders_to_excel():
    async with async_session() as session:
        # Получаем все заказы из базы данных
        orders = await session.execute(select(Order))
        orders = orders.scalars().all()
        
        # Создаем книгу Excel
        wb = Workbook()
        ws = wb.active

        # Добавляем заголовки столбцов
        ws.append(['Заказ №','Телефон','Вкус', 'Крепость', 'Время', 'Цена', 'Было', 'Стало'])

        # Добавляем данные о заказах
        for order in orders:
            ws.append([
                order.id, 
                order.phone_number,
                order.taste_id,  # Вам нужно будет заменить это на соответствие реальных значений в данных
                order.strength_id,  # Например, name вместо id, если у вас есть ссылка на другую таблицу
                order.time_order,
                order.price,
                order.old_bonus,
                order.new_bonus  # Преобразование в строку, если это объект datetime
            ])

        excel_filename = 'orders.xlsx'
        wb.save(excel_filename)
        
        return excel_filename
        


@router.message(F.text == 'Статистика')
async def view_orders(message: types.Document):
    
    # Получаем все заказы из базы данных
    excel_filename = await export_orders_to_excel()  # Сохраняем данные в Excel

        # Отправляем полученный файл
    with open(excel_filename, 'rb') as excel_file:
        await message.answer_document(document=FSInputFile('orders.xlsx'), caption='Все заказы в Excel файле')