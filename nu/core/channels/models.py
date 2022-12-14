from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID as PythonUUID

from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

from nu.db.base_class import Base

if TYPE_CHECKING:
    from nu.core.player.models import Character

__all__ = ["Channel", "ChannelCharacter", "ChannelMessage"]


class ChannelCharacter(Base):
    id: None = None  # type: ignore
    channel_id: PythonUUID = Column(ForeignKey("channel.id"), primary_key=True)
    character_id: PythonUUID = Column(ForeignKey("character.id"), primary_key=True)

    character: "Character" = relationship("Character")
    channel: "Channel" = relationship("Channel")


class Channel(Base):
    name = Column(String)
    description = Column(String)
    messages: list["ChannelMessage"] = relationship(
        "ChannelMessage", back_populates="channel", uselist=True
    )

    channel_characters: list["ChannelCharacter"] = relationship(
        "ChannelCharacter", back_populates="channel", uselist=True
    )

    @property
    def characters(self) -> list["Character"]:
        return [c.character for c in self.channel_characters]

    @property
    def character_ids(self) -> list[PythonUUID]:
        return [c.character_id for c in self.channel_characters]


class ChannelMessage(Base):
    message = Column(String)
    character_id: PythonUUID = Column(ForeignKey("character.id"))
    character: "Character" = relationship("Character")
    channel_id: PythonUUID = Column(ForeignKey("channel.id"))
    channel: "Channel" = relationship("Channel", back_populates="messages")
    system = Column(Boolean, default=False)
    timestamp: datetime = Column(TIMESTAMP(timezone=True), nullable=False)
