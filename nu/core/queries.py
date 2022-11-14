import strawberry

from nu.info import NuInfo

from .loaders import CharacterLoader, PlayerLoader
from .types import Character, Player


async def get_current_player(info: "NuInfo") -> Player | None:
    assert info.context.player, "Not logged in"
    return await info.context.loaders.get_loader(PlayerLoader).by_id(
        info.context.player.id
    )


async def get_characters(info: "NuInfo") -> list[Character]:
    return await info.context.loaders.get_loader(CharacterLoader).all()


@strawberry.type
class Query:
    me: Player = strawberry.field(resolver=get_current_player)
    characters: list[Character] = strawberry.field(resolver=get_characters)
