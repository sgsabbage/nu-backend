from sqlalchemy import select
from sqlalchemy.orm import with_parent

from nu.loaders import BaseLoader

from .models import Character, Player
from .types import Character as CharacterType
from .types import Player as PlayerType


class CharacterLoader(BaseLoader[Character, CharacterType]):
    model = Character
    type = CharacterType

    async def by_player(self, player: Player) -> list[CharacterType]:
        result = await self.session.execute(
            select(Character).where(with_parent(player, Player.characters))
        )
        chars = result.scalars().all()

        return [CharacterType.from_orm(c) for c in chars if await self.can_see(c)]

    async def can_see(self, obj: Character) -> bool:
        return True


class PlayerLoader(BaseLoader[Player, PlayerType]):
    model = Player
    type = PlayerType

    async def can_see(self, obj: Player) -> bool:
        return True
