from sqlalchemy import Column, String, Integer, BigInteger, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from apps.config.config import SQLALCHEMY_URL
from sqlalchemy import ForeignKey
from datetime import datetime
import random
from sqlalchemy import select

engine = create_async_engine(SQLALCHEMY_URL, echo=True)

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger)
    phone_number = Column(String)
    bonuce = Column(Integer)
    orders = relationship("Order", back_populates="user")

class Strength(Base):
    __tablename__ = 'strength'

    id = Column(String, primary_key=True)
    name = Column(String)
    tastes = relationship('Tastes', back_populates='strength')
    orders = relationship('Order', back_populates='strength')

class Tastes(Base):
    __tablename__ = 'taste'

    id = Column(String, primary_key=True)
    name = Column(String)
    strength_id = Column(Integer, ForeignKey('strength.id'))
    strength = relationship('Strength', back_populates='tastes')
    orders = relationship('Order', back_populates='taste')
    
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    id_order = Column(String, unique=True)
    phone_number = Column(String, ForeignKey('users.phone_number'))
    taste_id = Column(String, ForeignKey('taste.id'))
    strength_id = Column(String, ForeignKey('strength.id'))
    timestump = Column(DateTime, default=datetime.utcnow)
    bowl = Column(String)
    price = Column(Integer)
    old_bonus = Column(Integer)
    new_bonus = Column(Integer)
    time_order = Column(String)
    user = relationship("User", back_populates="orders")
    taste = relationship("Tastes", back_populates="orders")
    strength = relationship("Strength", back_populates="orders")

    @staticmethod
    async def create_new_order_id():
        async with async_session() as session:
            unique = False
            id_order = 0
            while not unique:
                id_order = random.randint(1000000, 9999999)
            # Проверяем, есть ли уже такой order_id в базе
                exists = await session.execute(select(Order).filter_by(id_order=id_order)) 
                res = exists.scalars().first()
                unique = not res
        
            return id_order




async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        