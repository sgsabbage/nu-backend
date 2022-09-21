import strawberry
from sqlalchemy import select

from nu.info import NuInfo

from .models import Player
from .types import Character as CharacterType
from .types import Player as PlayerType


async def get_current_player(info: "NuInfo") -> PlayerType:
    session = info.context.session
    result = await session.execute(
        select(Player).where(Player.id == info.context.player.id)
    )
    return PlayerType.from_orm(result.scalar_one())


async def get_characters(info: "NuInfo") -> list[CharacterType]:
    return await info.context.loaders.characters.all()


@strawberry.type
class Query:
    me: PlayerType = strawberry.field(resolver=get_current_player)
    characters: list[CharacterType] = strawberry.field(resolver=get_characters)
