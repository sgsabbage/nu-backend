from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from nu.core.player.models import Character as CharacterModel
from nu.plugin import BasePlugin

from .models import ChannelCharacter
from .queries import Query


class Plugin(BasePlugin):
    NAME = "channels"
    VERSION = "0.1.0"
    queries = [Query]

    @classmethod
    def install(cls) -> None:
        setattr(
            CharacterModel,
            "character_channels",
            relationship(ChannelCharacter, back_populates="character", uselist=True),
        )
        setattr(
            CharacterModel,
            "channels",
            association_proxy("character_channels", "channel"),
        )
