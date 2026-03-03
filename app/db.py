
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from sqlalchemy import String, Integer, Text, Boolean, ForeignKey, DateTime

from datetime import datetime, timezone
from sqlalchemy.sql import func

from typing import AsyncGenerator
import uuid
from sqlalchemy.dialects.postgresql import UUID
#from sqlalchemy import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi_users.db import SQLAlchemyUserDatabase,SQLAlchemyBaseUserTableUUID
from fastapi import Depends

DATABASE_URL= "sqlite+aiosqlite:///./test.db"

class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user" 
    posts = relationship(argument= "Post", back_populates="user")



class Post(Base):
    __tablename__= "post"

    id: Mapped[uuid.UUID]= mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID]= mapped_column(ForeignKey("user.id"))
    caption: Mapped[str]= mapped_column(Text)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(100), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="posts")

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit= False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session():
    async with async_session_maker() as session:
        yield session

async def get_user_db(session = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

