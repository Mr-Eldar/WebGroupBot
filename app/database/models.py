import os
from dotenv import load_dotenv
from _datetime import datetime

from sqlalchemy import ForeignKey, String, BigInteger, Boolean, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

load_dotenv()

engine = create_async_engine(url=os.getenv("DB_URL"),
                             echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    su: Mapped[str] = mapped_column(String(100), default='Ученик 4 группы.')
    level: Mapped[str] = mapped_column(String(50), default='Новичок')
    points: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[int] = mapped_column(Integer, default=0)
    completed_hw: Mapped[int] = mapped_column(Integer, default=0)
    expired_hw: Mapped[int] = mapped_column(Integer, default=0)


class UserTask(Base):
    __tablename__ = "user_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('tasks.id'))
    status: Mapped[str] = mapped_column(String, default='not started')
    created_at = mapped_column(DateTime, default=datetime.now)
    updated_at = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    task_name: Mapped[str] = mapped_column(String(300))
    task_description: Mapped[str] = mapped_column(String(2000))
    task_complete_time: Mapped[str] = mapped_column(String(100))
    task_materials: Mapped[str] = mapped_column(String(1000))
    points: Mapped[int] = mapped_column(BigInteger, default=0)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)