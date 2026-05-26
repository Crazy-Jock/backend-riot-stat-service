import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from pathlib import Path


BASE_DIRECTORY = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIRECTORY / ".env")
DATABASE_URL = f"postgresql+asyncpg://{os.getenv("USER_DB")}:{os.getenv("PASSWORD_DB")}@localhost:5432/RiotMetrica"

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass