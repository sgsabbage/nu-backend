from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Generic, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_parent
from sqlalchemy.util import asyncio
from strawberry.dataloader import DataLoader

import nu.graphql.types as types
import nu.models as models
from nu.db.base_class import Base


class Loaders:
    def __init__(self, session: AsyncSession, viewer: models.Player):
        self.session = session
        self.viewer = viewer
        self.rooms = RoomLoader(session, viewer)
        self.characters = CharacterLoader(session, viewer)
        self.channels = ChannelLoader(session, viewer)


def get_loaders(session: AsyncSession, viewer: models.Player) -> Loaders:
    return Loaders(session, viewer)


M = TypeVar("M", bound=Base)
T = TypeVar("T", bound=types.BaseType)  # type: ignore


def loader_function(
    type_class: Type[M], session: AsyncSession
) -> Callable[[list[UUID]], Coroutine[Any, Any, list[M | ValueError]]]:
    async def lookup(keys: list[UUID]) -> list[M | ValueError]:
        result = await session.execute(
            select(type_class).filter(type_class.id.in_(keys))
        )
        rows = result.scalars().all()
        return [
            next(
                (r for r in rows if r.id == k),
                ValueError(f"{k} does not exist"),
            )
            for k in keys
        ]

    return lookup


class BaseLoader(ABC, Generic[M, T]):
    model: Type[M]
    type: Type[T]

    def __init__(
        self,
        session: AsyncSession,
        viewer: models.Player,
    ):
        self.session = session
        self.viewer = viewer
        self.loader = DataLoader[UUID, M](load_fn=loader_function(self.model, session))

    async def by_id(self, id: UUID) -> Optional[T]:
        obj = await self.loader.load(id)
        return self.type.from_orm(obj) if await self.can_see(obj) else None

    @abstractmethod
    async def can_see(self, obj: M) -> bool:
        ...


class RoomLoader(BaseLoader[models.Room, types.Room]):
    model = models.Room
    type = types.Room

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._room_lock = asyncio.Lock()
        self._room_done = False
        self._known_rooms: list[models.Room] = []

    async def all(self) -> list[types.Room]:
        result = await self.session.execute(select(models.Room))
        rooms = result.scalars().all()

        return [types.Room.from_orm(r) for r in rooms if await self.can_see(r)]

    async def by_area(self, area: models.Area) -> list[types.Room]:
        result = await self.session.execute(
            select(models.Room).where(models.Room.area_id == area.id)
        )
        rooms = result.scalars().all()

        return [types.Room.from_orm(r) for r in rooms if await self.can_see(r)]

    async def can_see(self, obj: models.Room) -> bool:
        if obj not in await self.known_rooms:
            return False
        return True

    @property
    async def known_rooms(self) -> list[models.Room]:
        async with self._room_lock:
            if not self._room_done:
                # TODO: Tie this back to the correct known rooms list
                self._known_rooms = (
                    (await self.session.execute(select(models.Room))).scalars().all()
                )
                self._room_done = True
            return self._known_rooms


class CharacterLoader(BaseLoader[models.Character, types.Character]):
    model = models.Character
    type = types.Character

    async def all(self) -> list[types.Character]:
        result = await self.session.execute(select(models.Character))
        chars = result.scalars().all()

        return [types.Character.from_orm(c) for c in chars if await self.can_see(c)]

    async def by_player(self, player: models.Player) -> list[types.Character]:
        result = await self.session.execute(
            select(models.Character).where(
                with_parent(player, models.Player.characters)
            )
        )
        chars = result.scalars().all()

        return [types.Character.from_orm(c) for c in chars if await self.can_see(c)]

    async def can_see(self, obj: models.Character) -> bool:
        return True


class ChannelLoader(BaseLoader[models.Channel, types.Channel]):
    model = models.Channel
    type = types.Channel

    async def can_see(self, obj: models.Channel) -> bool:
        return True
