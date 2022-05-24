import asyncio
from typing import AsyncGenerator, Generator

import pytest
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, create_async_engine

from nu.core.config import settings
from nu.db.base_class import metadata


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Creates an instance of the default event loop for the test session.
    """

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def session_db() -> AsyncGenerator[AsyncConnection, None]:
    assert settings.SQLALCHEMY_DATABASE_URI
    url = make_url(settings.SQLALCHEMY_DATABASE_URI)
    url = url.set(drivername="postgresql+asyncpg")
    pg = url.set(database="postgres")
    engine_admin = create_async_engine(pg, pool_pre_ping=True, future=True, echo=False)

    async with engine_admin.connect() as conn:
        await conn.exec_driver_sql("ROLLBACK")
        await conn.exec_driver_sql("DROP DATABASE IF EXISTS test")
        await conn.exec_driver_sql("CREATE DATABASE test")

    await engine_admin.dispose()

    test_db = url.set(database="test")
    engine = create_async_engine(test_db, pool_pre_ping=True, future=True, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    async with engine.connect() as conn:
        yield conn


@pytest.fixture
async def db(session_db: AsyncConnection) -> AsyncGenerator[AsyncSession, None]:
    await session_db.begin()
    session = AsyncSession(bind=session_db)
    await session_db.begin_nested()
    yield session
    await session_db.rollback()
