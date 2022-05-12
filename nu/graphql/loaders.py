from dataclasses import dataclass
from typing import Any, Callable, Coroutine
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from nu.models import Area, Channel, Character


def load_characters(
    session: AsyncSession,
) -> Callable[[list[UUID]], Coroutine[Any, Any, list[Character | None]]]:
    async def lookup(keys: list[UUID]) -> list[Character | None]:
        result = await session.execute(select(Character).filter(Character.id.in_(keys)))
        chars = result.scalars().all()
        return [next((c for c in chars if c.id == k), None) for k in keys]

    return lookup


def load_areas(
    session: AsyncSession,
) -> Callable[[list[UUID]], Coroutine[Any, Any, list[Area | None]]]:
    async def lookup(keys: list[UUID]) -> list[Area | None]:
        result = await session.execute(select(Area).filter(Area.id.in_(keys)))
        areas = result.scalars().all()
        return [next((a for a in areas if a.id == k), None) for k in keys]

    return lookup


def load_channels(
    session: AsyncSession,
) -> Callable[[list[UUID]], Coroutine[Any, Any, list[Channel | None]]]:
    async def lookup(keys: list[UUID]) -> list[Channel | None]:
        result = await session.execute(select(Channel).filter(Channel.id.in_(keys)))
        channels = result.scalars().all()
        return [next((c for c in channels if c.id == k), None) for k in keys]

    return lookup


@dataclass
class Loaders:
    characters: DataLoader[UUID, Character]
    areas: DataLoader[UUID, Area]
    channels: DataLoader[UUID, Channel]


def get_loaders(session: AsyncSession) -> Loaders:
    return Loaders(
        characters=DataLoader(load_fn=load_characters(session)),
        areas=DataLoader(load_fn=load_areas(session)),
        channels=DataLoader(load_fn=load_channels(session)),
    )
