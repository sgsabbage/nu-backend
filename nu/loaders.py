from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Generic, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

import nu.types as types
from nu.core.player.models import Player
from nu.db.base_class import Base


class Loaders:
    def __init__(self, session: AsyncSession, viewer: Player):

        from nu.core.grid.loaders import AreaLoader, RoomLoader
        from nu.core.player.loaders import CharacterLoader, PlayerLoader

        self.session = session
        self.viewer = viewer
        self.areas = AreaLoader(session, viewer)
        self.rooms = RoomLoader(session, viewer)
        self.characters = CharacterLoader(session, viewer)
        self.players = PlayerLoader(session, viewer)
        # self.channels = ChannelLoader(session, viewer)


def get_loaders(session: AsyncSession, viewer: Player) -> Loaders:
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
        viewer: Player,
    ):
        self.session = session
        self.viewer = viewer
        self.loader = DataLoader[UUID, M](load_fn=loader_function(self.model, session))

    async def by_id(self, id: UUID) -> Optional[T]:
        obj = await self.loader.load(id)
        return self.type.from_orm(obj) if await self.can_see(obj) else None

    async def all(self) -> list[T]:
        result = await self.session.execute(select(self.model))
        items = result.scalars().all()

        self.loader.prime_many(data={i.id: i for i in items})

        return [self.type.from_orm(i) for i in items if await self.can_see(i)]

    @abstractmethod
    async def can_see(self, obj: M) -> bool:
        ...


#


# class ChannelLoader(BaseLoader[models.Channel, types.Channel]):
#     model = models.Channel
#     type = types.Channel

#     async def can_see(self, obj: models.Channel) -> bool:
#         return True
