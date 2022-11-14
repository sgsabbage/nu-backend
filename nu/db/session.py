from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from nu.core.config import settings

assert settings.SQLALCHEMY_DATABASE_URI
url = make_url(settings.SQLALCHEMY_DATABASE_URI)
url = url.set(drivername="postgresql+asyncpg")
engine = create_async_engine(url, pool_pre_ping=True, future=True, echo=False)
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    autoflush=False, expire_on_commit=False, bind=engine
)
