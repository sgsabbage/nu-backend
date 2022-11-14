from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from nu.core.models import Player

from .loaders import Loaders


@dataclass
class PlayerContext(BaseContext):
    player: Player


@dataclass
class Context(BaseContext):
    player: Player
    session: AsyncSession
    loaders: Loaders
