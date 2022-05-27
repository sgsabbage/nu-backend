from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from .graphql.loaders import Loaders
from .models import Player


@dataclass
class PlayerContext(BaseContext):
    player: Player


@dataclass
class Context(BaseContext):
    player: Player
    session: AsyncSession
    loaders: Loaders
