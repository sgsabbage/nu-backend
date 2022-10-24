import strawberry

from nu.types import BaseType, HasModel

from .models import CharacterHealth as CharacterHealthModel
from .protocols import HasHealth


@strawberry.type
class CharacterHealth(BaseType[CharacterHealthModel]):
    current_hp: int
    total_hp: int


def get_health(root: HasModel) -> CharacterHealth | None:
    assert isinstance(root.model, HasHealth)
    if root.model.health is None:
        return None
    return CharacterHealth.from_orm(root.model.health)
