import re
from aiogram import types
from apps.config.config import HOOKAH_MASTER_ID
from apps.database.models import Order, User, async_session
from apps.keyboards.keyboards import *
from apps.states.States import Hookah, Newsletter, Request, Request_Master
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from aiogram.types import FSInputFile
from openpyxl import Workbook
from sqlalchemy import update



router = Router()





# HOOKAH MASTER PANNEL
@router.message(F.text == 'Посмотреть информацию по 1 пользователю')
async def info_user_for_master(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id == HOOKAH_MASTER_ID:
        await state.set_state(Request_Master.phone_info)
   
        await message.answer('Введите номер телефона пользователя: ')
    else: 
        await message.answer('Я тебя не понимаю')


async def export_order_user_to_excel_for_master(phone_number):
    # Получаем все заказы из базы данных для конкретного номера телефона
    async with async_session() as session:
        balance = await session.execute(select(Order.bonuce).where(Order.phone_number == phone_number))
        res = balance.scalar()
        result = await session.execute(select(Order.phone_number, Order.taste_id, Order.strength_id, Order.time_order, Order.bowl, Order.price, Order.old_bonus, Order.new_bonus).where(Order.phone_number == phone_number))
        orders = result.all()
        
        # Создаем книгу Excel
        wb = Workbook()
        ws = wb.active

        # Добавляем заголовки столбцов
        ws.append(['Телефон', 'Вкус', 'Крепость', 'Время', 'Цена', 'Бонусы'])
        
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
        
        excel_filename = 'order_user_for_master.xlsx'
        wb.save(excel_filename)
        return excel_filename



@router.message(Request_Master.phone_info)
async def info_user_master(message: Message, state: FSMContext):
    
    phone_number = message.text
    excel_filename = await export_order_user_to_excel_for_master(phone_number)  # Сохраняем данные в Excel
    if re.fullmatch(r'\+\d{11}', phone_number) or re.fullmatch(r'\d{11}', phone_number):
    # Отправляем полученный файл
        with open(excel_filename, 'rb') as excel_file:
            await message.answer_document(document=FSInputFile('order_user_for_master.xlsx'), caption='Все заказы в Excel файле', reply_markup=main_hookah_master)                         
        await state.clear()
    else:
        await message.answer('Введите коректный номер телефона:')



@router.message(F.text == 'Изменить баланс бонусов')
async def change_bonus(message: Message, state: FSMContext):
    await state.set_state(Request_Master.phone_balance)
    await message.answer('Введите номер пользователя:') 

@router.message(Request_Master.phone_balance)
async def balance(message: Message, state: FSMContext):
    async with async_session() as session:
        phone = message.text

        balanc = await session.execute(select(User.bonuce).where(User.phone_number == phone))
        res = balanc.scalar()

        await state.update_data(phone_balance=message.text)
        await state.set_state(Request_Master.change_balance)

        if re.fullmatch(r'\+\d{11}', phone) or re.fullmatch(r'\d{11}', phone):
            await message.answer(f'Сейчас у пользователя {res} бонусов')
            await message.answer('Введите нужное кол-во бонусов: ')
        else:
            await message.answer('Введите коректный номер телефона')


@router.message(Request_Master.change_balance)
async def change_balance_(message: Message, state: FSMContext):
    

    await state.update_data(change_balance=message.text)
    await state.set_state(Request_Master.id)
    # data = await state.get_data()
        # phone = data.get('phone_balance')
        # new_balance = int(message.text)
        
        # balance_now = await session.execute(select(User.bonuce).where(User.phone_number == phone))
        # res = balance_now.scalar()
        
        
        # await session.execute(update(User).where(User.phone_number == phone).values(bonuce=new_balance))
        # await session.execute(update(Order).where(Order.phone_number == phone).values(new_bonus=new_balance))
        # await session.commit()
              # Очистим состояние после выполнения операции
    await message.answer('Введите ID заказа:')

@router.message(Request_Master.id)
async def change_balance_func(message: Message, state: FSMContext):
    async with async_session() as session:
        await state.update_data(id=message.text)
        data = await state.get_data()
        phone = data.get('phone_balance')
        new_balance = data.get('change_balance')
        id = data.get('id')

        balance_now = await session.execute(select(User.bonuce).where(User.phone_number == phone))
        res = balance_now.scalar()
        
        
        await session.execute(update(User).where(User.phone_number == phone).values(bonuce=new_balance))
        await session.execute(update(Order).where(Order.id_order==id).values(new_bonus=new_balance))
        await session.commit()

        await message.answer(f'Баланс бонусов пользовтеля {phone} изменен на {new_balance}')





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
    
@router.message(F.text == 'Посмотреть информацию по всем пользователям')
async def view_orders_all(message: types.Document):
    
    # Получаем все заказы из базы данных
    excel_filename = await export_orders_to_excel()  # Сохраняем данные в Excel

        # Отправляем полученный файл
    with open(excel_filename, 'rb') as excel_file:
        await message.answer_document(document=FSInputFile('orders.xlsx'), caption='Все заказы в Excel файле')



        
        