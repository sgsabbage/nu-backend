from sqlalchemy.orm import relationship

import nu.core.player.types as coretypes
from nu.core.player.models import Character as CharacterModel
from nu.plugins.health.models import CharacterHealth
from nu.plugins.health.types import get_health

NAME = "health"
VERSION = "0.1.0"


def install_plugin() -> None:
    setattr(
        CharacterModel,
        "health",
        relationship(
            CharacterHealth,
            back_populates="character",
            lazy="selectin",
            uselist=False,
        ),
    )

    coretypes.Character.add_extra_field("health", get_health)
