from dataclasses import dataclass
from typing import Any, Callable, Coroutine

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from nu.models import Character


def load_characters(
    session: AsyncSession,
) -> Callable[[list[str]], Coroutine[Any, Any, list[Character | None]]]:
    async def lookup(keys: list[str]) -> list[Character | None]:
        result = await session.execute(select(Character).filter(Character.id.in_(keys)))
        chars = result.scalars().all()
        return [next((c for c in chars if c.id == k), None) for k in keys]

    return lookup


@dataclass
class Loaders:
    characters: DataLoader[str, Character]


def get_loaders(session: AsyncSession) -> Loaders:
    return Loaders(characters=DataLoader(load_fn=load_characters(session)))
