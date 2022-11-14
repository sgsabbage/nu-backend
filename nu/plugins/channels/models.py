from datetime import datetime
from uuid import UUID

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)

from nu.core.models import Character
from nu.db.base_class import BaseMixin, convention, pkuuid

__all__ = ["Channel", "ChannelCharacter", "ChannelMessage"]

metadata = MetaData(naming_convention=convention, schema="plugin_channels")


class Base(BaseMixin, MappedAsDataclass, DeclarativeBase):
    metadata = metadata


class ChannelCharacter(Base):
    character: Mapped["Character"] = relationship(Character)
    channel: Mapped["Channel"] = relationship("Channel")

    channel_id: Mapped[UUID] = mapped_column(
        ForeignKey("channel.id"), primary_key=True, default=None
    )
    character_id: Mapped[UUID] = mapped_column(
        ForeignKey(Character.id), primary_key=True, default=None
    )


class Channel(Base):
    id: Mapped[pkuuid]
    name: Mapped[str]
    description: Mapped[str]
    messages: Mapped[list["ChannelMessage"]] = relationship(
        "ChannelMessage", back_populates="channel", default_factory=list
    )

    channel_characters: Mapped[list["ChannelCharacter"]] = relationship(
        "ChannelCharacter", back_populates="channel", default_factory=list
    )

    characters = association_proxy("channel_characters", "character")

    @property
    def character_ids(self) -> list[UUID]:
        return [c.character_id for c in self.channel_characters]


class ChannelMessage(Base):
    id: Mapped[pkuuid]
    message: Mapped[str]
    character_id: Mapped[UUID] = mapped_column(ForeignKey(Character.id))
    character: Mapped["Character"] = relationship(Character)
    channel_id: Mapped[UUID] = mapped_column(ForeignKey("channel.id"))
    channel: Mapped["Channel"] = relationship("Channel", back_populates="messages")
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    system: Mapped[bool] = mapped_column(Boolean, default=False)
