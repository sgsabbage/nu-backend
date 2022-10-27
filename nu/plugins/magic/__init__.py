from sqlalchemy.orm import relationship

import nu.core.player.types as coretypes
from nu.core.player.models import Character as CharacterModel
from nu.plugin import BasePlugin
from nu.plugins.magic.models import CharacterMagic
from nu.plugins.magic.types import get_magic


class Plugin(BasePlugin):

    NAME = "magic"
    VERSION = "0.2.0"

    @classmethod
    def install(cls) -> None:
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
