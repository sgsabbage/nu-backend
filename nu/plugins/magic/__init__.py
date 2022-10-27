from sqlalchemy.orm import relationship

import nu.core.player.types as coretypes
from nu.core.player.models import Character as CharacterModel
from nu.plugins.magic.models import CharacterMagic
from nu.plugins.magic.types import get_magic

NAME = "magic"
VERSION = "0.2.0"


def install_plugin() -> None:
    setattr(
        CharacterModel,
        "magic",
        relationship(
            CharacterMagic,
            back_populates="character",
            lazy="selectin",
            uselist=False,
        ),
    )

    coretypes.Character.add_extra_field("magic", get_magic)
