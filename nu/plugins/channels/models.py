import re
from datetime import datetime
from typing import Any
from uuid import UUID as PythonUUID

from sqlalchemy import Boolean, Column, ForeignKey, MetaData, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import as_declarative, declared_attr, relationship

from nu.core.player.models import Character
from nu.db.base_class import convention

__all__ = ["Channel", "ChannelCharacter", "ChannelMessage"]

metadata = MetaData(naming_convention=convention, schema="plugin_channels")


@as_declarative(metadata=metadata)
class Base:
    id: Any
    id = Column(
        UUID(as_uuid=True),
        server_default=text("uuid_generate_v4()"),
        primary_key=True,
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """Convert CamelCase class name to underscores_between_words
        table name."""
        name = cls.__name__
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class ChannelCharacter(Base):
    id: None = None
    channel_id: PythonUUID = Column(ForeignKey("channel.id"), primary_key=True)
    character_id: PythonUUID = Column(ForeignKey(Character.id), primary_key=True)

    character: "Character" = relationship(Character)
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
    character_id: PythonUUID = Column(ForeignKey(Character.id))
    character: "Character" = relationship(Character)
    channel_id: PythonUUID = Column(ForeignKey("channel.id"))
    channel: "Channel" = relationship("Channel", back_populates="messages")
    system = Column(Boolean, default=False)
    timestamp: datetime = Column(TIMESTAMP(timezone=True), nullable=False)
