import asyncio
from typing import AsyncGenerator

import pytest
from sqlalchemy import func, select
from sqlalchemy.engine import make_url
from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, create_async_engine

from nu.core.config import settings
from nu.db.base_class import metadata
from nu.models import Player


async def test_is_this_true(db: AsyncSession) -> None:
    u = Player(username="test1")
    db.add(u)
    await db.commit()

    assert True


async def test_this_is_falsesdagsg(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsevcbvcbcxea(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falseahnag(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsefgafdgdag(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsesadfdsaf(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsedfhfdsh(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falseadfhfdhddsfrdsf(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsefhafhfd(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsefdhfdhd(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falseadsfdfs(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsevcbcn(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsezcxv(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsedsagngcxz(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falseasdfngn(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsesahmsdg(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falseahfhfdhdfh(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsecxvcvc(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsezxcxzcxzc(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falseaa(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsehhhhhh(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falseaffhfh(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falseasfasd(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falseasdsad(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_falsexcs(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_false215151(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_false47311(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_false57547(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_false32(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_false213213(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_false21321(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True


async def test_this_is_false2(db: AsyncSession) -> None:
    u = Player(username="test2")
    db.add(u)
    await db.commit()
    u = Player(username="test1")
    db.add(u)
    await db.commit()
    assert True
