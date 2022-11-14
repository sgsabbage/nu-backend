from typing import Protocol, runtime_checkable

from sqlalchemy.orm import Mapped

from .models import Channel, ChannelCharacter


@runtime_checkable
class CharacterWithChannels(Protocol):
    character_channels: Mapped[ChannelCharacter]
    channels: Mapped[Channel]
