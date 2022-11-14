from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Generic, Optional, Protocol, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

import nu.types as types
from nu.core.models import Player

L = TypeVar("L", bound="BaseLoader")  # type: ignore


class Loaders:
    def __init__(
        self, session: AsyncSession, viewer: Player, loader_classes: list[Type[L]]
    ):
        self._loaders: list["BaseLoader[Any, Any]"] = []

        self.session = session
        self.viewer = viewer

        for cls in loader_classes:
            self._loaders.append(cls(session, viewer))

    def get_loader(self, t: Type[L]) -> L:
        for loader in self._loaders:
            if isinstance(loader, t):
                break
        else:
            loader = t(self.session, self.viewer)
            self._loaders.append(loader)
        return loader


def get_loaders(
    session: AsyncSession, viewer: Player, loader_classes: list[Type[L]]
) -> Loaders:
    return Loaders(session, viewer, loader_classes)


class HasID(Protocol):
    id: Any


M = TypeVar("M", bound=HasID)
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
