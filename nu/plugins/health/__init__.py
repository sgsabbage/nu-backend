import strawberry
from sqlalchemy.orm import relationship

import nu.core.player.types as coretypes
from nu.core.player.models import Character as CharacterModel

from .types import get_health

setattr(
    CharacterModel,
    "health",
    relationship(
        "CharacterHealth",
        back_populates="character",
        lazy="selectin",
        uselist=False,
    ),
)

coretypes.Character.add_extra_field("health", get_health)
