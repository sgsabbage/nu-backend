import strawberry

from nu.types import BaseType, HasModel

from .models import CharacterMagic as CharacterMagicModel
from .protocols import HasMagic


@strawberry.type
class CharacterMagic(BaseType[CharacterMagicModel]):
    current_mp: int
    total_mp: int

    @strawberry.field
    async def spells_known(self) -> list[str]:
        return ["Fireball", "Burning Hands"]


def get_magic(root: HasModel) -> CharacterMagic | None:
    assert isinstance(root.model, HasMagic)
    if root.model.magic is None:
        return None
    return CharacterMagic.from_orm(root.model.magic)
