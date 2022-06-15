from __future__ import annotations

from typing import Any, Callable, Coroutine, Generic, Optional, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

import nu.graphql.types as types
from nu.models import Area, Channel, Character
from nu.models.map import Room
from nu.models.player import Player


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


def load_rooms(
    session: AsyncSession,
) -> Callable[[list[UUID]], Coroutine[Any, Any, list[Room | ValueError]]]:
    async def lookup(keys: list[UUID]) -> list[Room | ValueError]:
        result = await session.execute(select(Room).filter(Room.id.in_(keys)))
        rooms = result.scalars().all()
        return [
            next(
                (r for r in rooms if r.id == k),
                ValueError(f"{k} does not exist"),
            )
            for k in keys
        ]

    return lookup


class Loaders:
    characters: DataLoader[UUID, Character]
    areas: DataLoader[UUID, Area]
    channels: DataLoader[UUID, Channel]

    def __init__(self, session: AsyncSession, viewer: Player):
        self.session = session
        self.viewer = viewer
        self.rooms = RoomLoader(session, viewer, load_rooms)


def get_loaders(session: AsyncSession, viewer: Player) -> Loaders:
    return Loaders(session, viewer)


T = TypeVar("T")


class BaseLoader(Generic[T]):
    def __init__(
        self,
        session: AsyncSession,
        viewer: Player,
        loader_fn: Callable[
            [AsyncSession],
            Callable[[list[UUID]], Coroutine[Any, Any, list[T | ValueError]]],
        ],
    ):
        self.session = session
        self.viewer = viewer
        self.loader = DataLoader[UUID, T](load_fn=loader_fn(session))


class RoomLoader(BaseLoader[types.Room]):
    async def all(self) -> list[types.Room]:
        result = await self.session.execute(select(Room))
        rooms = result.scalars().all()

        return [types.Room.from_orm(r) for r in rooms if self.can_see(r)]

    async def by_id(self, id: UUID) -> Optional[types.Room]:
        room = await self.loader.load(id)
        return types.Room.from_orm(room) if self.can_see(room) else None

    async def by_area(self, area: Area) -> list[types.Room]:
        result = await self.session.execute(select(Room).where(Room.area_id == area.id))
        rooms = result.scalars().all()

        return [types.Room.from_orm(r) for r in rooms if self.can_see(r)]

    def can_see(self, room: Room) -> bool:
        return False
