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








@router.message(CommandStart())
async def cmd_start(message: Message):
    
    user_id = message.from_user.id
    if user_id in ADMIN_ID:
        await message.answer('Вы авторизовались как администратор, поделитесь своим номером телефона:', reply_markup=phone_number_user)
    if user_id == HOOKAH_MASTER_ID:
        await message.answer('Вы авторизовались как кальянный мастер', reply_markup=main_hookah_master)
    else:
        await message.answer(
            'Привет, тебя приветсвует бот, который будет рад помочь тебе провести твой отдых комфортно.'
            ''
            'Для правильной работы бота, вам нужно поделиться своим номером телефона. Нажмите на кнопку снизу',
            reply_markup=phone_number_user)
    






# Contact
@router.message(F.contact)
async def info_contact(message: Message):
    user_id = message.from_user.id
    contact = message.contact
    phone_num = contact.phone_number
    async with async_session() as session:
        # Попытка найти пользователя в базе данных по Telegram ID
        existing_user = await session.execute(select(User).where(User.tg_id == user_id))
        existing_user = existing_user.scalars().first()
        if existing_user:
            if user_id in ADMIN_ID:
                await message.answer(f"Ваш номер телефона {phone_num} подтвержден.", reply_markup=main)
            else:
                await message.answer(f"Спасибо, ваш номер телефона {phone_num} был получен!", reply_markup=main)
        else:
            bonuce_start = 0  # Начальное количество бонусных баллов для нового пользователя
            new_user = User(tg_id=user_id, phone_number=phone_num, bonuce=bonuce_start)
            session.add(new_user)
            await session.commit()  # Фиксируем нового пользователя в базе данных
            await message.answer(f"Спасибо, ваш номер телефона {phone_num} был зарегистрирован!", reply_markup=main)

    #await rq.get_user(message.from_user.id, phone_number, bonuce_start)
    # if user_id in ADMIN_ID:
    #     await message.answer(f"Спасибо, ваш номер телефона {phone_number} был получен!", reply_markup=main_admin)
    # else:
    #     await message.answer(f"Спасибо, ваш номер телефона {phone_number} был получен!", reply_markup=main)






@router.message(F.text == "Заказать кальян")
async def offer(message: Message):
    await message.answer("Выберите тип чаши кальяна", reply_markup=bowl_keybord)

# HOOKAH BOWL
@router.callback_query(F.data == 'regular_bowl')
async def choose_bowl(callback: CallbackQuery, state: FSMContext):
    await state.update_data(hookah_bowl='Обычная')
    await callback.answer()
    await callback.message.edit_text('Выберите крепость кальяна:', reply_markup=await strength_keyboard())

@router.callback_query(F.data == 'grapefruit_bowl')
async def choose_bowl(callback: CallbackQuery, state: FSMContext):
    await state.update_data(hookah_bowl='Грейпфрут')
    await callback.answer()
    await callback.message.edit_text('Выберите крепость кальяна:', reply_markup=await strength_keyboard())




# HOOKAH STRENGTH
@router.callback_query(F.data=='low')
async def hookah_strength(callback: CallbackQuery, state: FSMContext):
    await state.update_data(strength='Легкий')
    await callback.answer()
    await callback.message.edit_text('Выберите вкус:', reply_markup=await taste_keyboard())


@router.callback_query(F.data=='medium')
async def hookah_strength(callback: CallbackQuery, state: FSMContext):
    await state.update_data(strength='Средний')
    await callback.answer()
    await callback.message.edit_text('Выберите вкус:', reply_markup=await taste_keyboard())

    
@router.callback_query(F.data=='strong')
async def hookah_strength(callback: CallbackQuery, state: FSMContext):
    await state.update_data(strength='Крепкий')
    await callback.answer()
    await callback.message.edit_text('Выберите вкус:', reply_markup=await taste_keyboard())



# HOOKAH TASTE
@router.callback_query(F.data == 'berry')
async def hookah_taste(callback: CallbackQuery, state: FSMContext):
    await state.update_data(taste_hookah='Ягодный')
    await state.set_state(Hookah.time_order)
    data = await state.get_data()
    await callback.answer()
    await callback.message.edit_text(f'Ваш заказ\nЧаша:{data['hookah_bowl']}\nВкус: {data["taste_hookah"]}\nКрепость: {data["strength"]}\nНапишите к какому времени вас ждать(в формате 00:00):')



@router.callback_query(F.data == 'fruit')
async def hookah_taste(callback: CallbackQuery, state: FSMContext):
    await state.update_data(taste_hookah='Фруктовый')
    await state.set_state(Hookah.time_order)
    data = await state.get_data()
    await callback.answer()
    await callback.message.edit_text(f'Ваш заказ\nЧаша:{data['hookah_bowl']}\nВкус: {data["taste_hookah"]}\nКрепость: {data["strength"]}\nНапишите к какому времени вас ждать(в формате 00:00):')


@router.callback_query(F.data == 'citrus')
async def hookah_taste(callback: CallbackQuery, state: FSMContext):
    await state.update_data(taste_hookah='Цитрусовый')
    await state.set_state(Hookah.time_order)
    data = await state.get_data()
    await callback.answer()
    await callback.message.edit_text(f'Ваш заказ\nЧаша:{data['hookah_bowl']}\nВкус: {data["taste_hookah"]}\nКрепость: {data["strength"]}\nНапишите к какому времени вас ждать(в формате 00:00):')


@router.callback_query(F.data == 'other')
async def other(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Hookah.other_taste)
    await callback.answer()
    await callback.message.answer('Введите ваш вкус:')



@router.message(Hookah.other_taste)
async def other_data(message: Message, state: FSMContext):
    await state.update_data(taste_hookah=message.text)
    await state.set_state(Hookah.time_order)
    data = await state.get_data()
    await message.answer(f'Ваш заказ\nЧаша:{data['hookah_bowl']}\nВкус: {data["taste_hookah"]}\nКрепость: {data["strength"]}\nНапишите к какому времени вас ждать(в формате 00:00):')






@router.message(Hookah.time_order)
async def time_order(message: Message, state: FSMContext):
    
    # Сначала обновляем состояние с введенным временем
    await state.update_data(time_order=message.text)
    
    # Проверяем, что введенное время соответствует формату HH:MM
    if re.match(r'^\d{2}:\d{2}$', message.text):
        # Получаем данные из state после того, как они были обновлены
        data = await state.get_data()
        time_order = data['time_order']  # Теперь переменная time_order определена корректно
        
        # Проверяем корректность минут
        minutes = time_order[3:]
        if int(minutes) > 59:
            await message.answer('Ты не правильно указал время, попробуй еще раз:')
        else:
        
        # Код для валидного времени
            taste_hookah = data['taste_hookah']
            strength = data['strength']
            bowl = data.get('hookah_bowl')
        
            await message.answer(f'Ваш заказ\nЧаша: {bowl}\nВкус: {taste_hookah}\nКрепость: {strength}\nВремя: {time_order}', reply_markup=confirm_orders)
    else:
        # Если формат не соответствует HH:MM, просим пользователя ввести время заново
        await message.answer('Пожалуйста, введите время в формате HH:MM, где HH - часы, MM - минуты.')




#BACK TO OFFER

@router.callback_query(F.data == 'back_to_offer')
async def back_to_offer(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("Выберите уровень крепости кальяна", reply_markup=await strength_keyboard())







# CALL THE HOOKAH MAN
@router.message(F.text == 'Позвать кальянного мастера')
async def call_hookah_man(message: Message):
    async with async_session() as session:
        tg_id = message.from_user.id
        phone_number = await session.scalar(select(User.phone_number).where(User.tg_id == message.from_user.id))

        message_to_master = f'Вас зовут - {phone_number}'
        await bt.send_message(HOOKAH_MASTER_ID, message_to_master)
        await message.answer('Ожидайте, скоро мастер к вам подойдет', reply_markup=main)







# CONFIRM THE ORDER

@router.callback_query(F.data == 'confirm')
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        
        data = await state.get_data()

        strength = data.get('strength')
        taste = data.get('taste_hookah')
        time = data.get('time_order')
        bowl = data.get('hookah_bowl')
        bon = data.get('change_balance')
        await callback.answer()
        await callback.message.answer('Ваш заказ оформлен.', reply_markup=main)

        day_time = ['12', '13', '14', '15', '16'] 
        regular_time = ['17', '18', '19', '20', '21', '22', '23']
        price = 0
        if bowl == 'Грейфпруфт' and time_order[:2] in regular_time:
            price = 1700
        if time[:2] in day_time:
            price = 650
        if time[:2] in regular_time:
            price = 1300
        if bowl == 'Грейфпруфт' and time_order[:2] in regular_time:
            price = 1700
        order_id = await Order.create_new_order_id()
        phone_number = await session.scalar(select(User.phone_number).where(User.tg_id == callback.from_user.id))
        bal = await session.scalar(select(User.bonuce).where(User.phone_number == phone_number))
        user = await session.scalar(select(User).where(User.tg_id == callback.from_user.id, User.phone_number == phone_number))
        new_order = await rq.create_order(id_order=order_id,phone_number=phone_number,price=price, bowl = bowl, taste_id=taste, strength_id=strength, time_order = time, old_bonus=bal, new_bonus=bal)
        
        await session.commit()
        message_text = f"Новый заказ:\nId:{order_id}\nЧаша: {bowl}\nКрепость: {strength}\nВкус: {taste}\nВремя: {time}\nНомер телефона: {phone_number}"
        await bt.send_message(HOOKAH_MASTER_ID, message_text)
        session.add(new_order)
        await state.clear()





@router.callback_query(F.data == 'use_bonuse')
async def use_or_not(callback: CallbackQuery):
    async with async_session() as session:

        phone_number = await session.scalar(select(User.phone_number).where(User.tg_id == callback.from_user.id))
        balance = await session.scalar(select(User.bonuce).where(User.phone_number == phone_number)) 
        await callback.answer()
        await callback.message.answer(f'На вашем счету {balance} бонусов.\n Использовать бонусы?', reply_markup=use_bon)
        



@router.callback_query(F.data == 'yes')
async def use_bonuse(callback: CallbackQuery, state: FSMContext):
    async with async_session() as session:
        data = await state.get_data()

        strength = data.get('strength')
        taste = data.get('taste_hookah')
        time = data.get('time_order')
        bowl = data.get('hookah_bowl')
        order_id = await Order.create_new_order_id()
        balance = await session.scalar(select(User.bonuce).where(User.tg_id == callback.from_user.id))  
        phone_number = await session.scalar(select(User.phone_number).where(User.tg_id == callback.from_user.id))
        user = await session.scalar(select(User).where(User.tg_id == callback.from_user.id, User.phone_number == phone_number))
        await callback.answer()
        await callback.message.answer(f'Ваш заказ оформлен. ID:{order_id}', reply_markup=main)
        message_text = f"Новый заказ:\nId:{order_id}\nЧаша: {bowl}\nКрепость: {strength}\nВкус: {taste}\nВремя: {time}\nИспользование бонусов: {balance}\nНомер телефона: {phone_number}"
        for i in HOOKAH_MASTER_ID:
            await bt.send_message(i, message_text)
        day_time = ['12', '13', '14', '15', '16'] 
        regular_time = ['17', '18', '19', '20', '21', '22', '23']
        if bowl == 'Грейфпруфт' and time_order[:2] in regular_time:
            price = 1700
        if time[:2] in day_time:
            price = 650
        if time[:2] in regular_time:
            price = 1300
        if bowl == 'Грейфпруфт' and time_order[:2] in regular_time:
            price = 1700
        
        new_order = await rq.create_order(id_order=order_id,phone_number=phone_number,price=price, bowl = bowl, taste_id=taste, strength_id=strength, time_order = time)
        
        session.add(new_order)

        await session.commit()
        
        
@router.callback_query(F.data == 'no')
async def no_use_bonuse(callback: CallbackQuery, state: FSMContext):
    
    data = await state.get_data()

    strength = data.get('strength')
    taste = data.get('taste_hookah')
    time = data.get('time_order')
    bowl = data.get('hookah_bowl')
    await callback.answer()
    await callback.message.answer(f'Ваш заказ\nЧаша: {bowl}\nВкус: {taste}\nКрепость: {strength}\nВремя: {time}\n', reply_markup=confirm_orders)



@router.message(F.text == 'Узнать о бонусах')
async def info_bonuce(message: Message):
    async with async_session() as session:
        balance = await session.scalar(select(User.bonuce).where(User.tg_id == message.from_user.id))
        await message.answer(f'Ваш баланс бонусов: {balance}', reply_markup=bonuses)

@router.message(F.text == 'Как начисляются бонусы?')
async def how_bonuses(message: Message):
    await message.answer('1 бонус = 1 рубль\nС каждого заказа на ваш баланс попадает количество бонусов равное 10% от заказа', reply_markup=main)






