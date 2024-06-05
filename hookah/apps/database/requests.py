import datetime
import random
from apps.database.models import User, Strength, Order, Tastes, async_session
from sqlalchemy import select



async def get_user(tg_id: int, phone_number: str, bonuce: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id, User.phone_number == phone_number, User.bonuce == bonuce))
        if not user:
            new_user = User(tg_id=tg_id, phone_number=phone_number, bonuce=bonuce)
            session.add(new_user)
            await session.commit()




async def get_strength():
    async with async_session() as session:
        result = await session.scalars(select(Strength))
        return result

async def get_tastes():
    async with async_session() as session:
        result = await session.scalars(select(Tastes))
        return result









async def create_order(id_order: int,phone_number: str, price: int, bowl: str, taste_id: str, time_order: str, strength_id: int, old_bonus: int, new_bonus: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.phone_number == phone_number))
        user = result.scalars().first()

        

        new_order = Order(id_order=id_order,phone_number=phone_number, price=price, bowl=bowl,taste_id=taste_id, strength_id=strength_id, 
                          timestump = datetime.datetime.now(), time_order=time_order, old_bonus=old_bonus, new_bonus=new_bonus)
        session.add(new_order)
        await session.commit()
        return new_order









