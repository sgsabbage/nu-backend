from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from nu.core.models import Character as CharacterModel
from nu.core.types import Character as CharacterType
from nu.plugin import BasePlugin

from .models import ChannelCharacter
from .queries import Query
from .resolvers import get_character_channels


class Plugin(BasePlugin):
    NAME = "channels"
    VERSION = "0.1.0"
    queries = [Query]

    @classmethod
    def install(cls) -> None:
        CharacterModel.character_channels = relationship(
            ChannelCharacter, back_populates="character", uselist=True
        )
        CharacterModel.channels = association_proxy("character_channels", "channel")

        CharacterType.add_extra_field("channels", get_character_channels)
