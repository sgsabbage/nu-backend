from __future__ import annotations

from typing import TYPE_CHECKING, List
from uuid import UUID as PythonUUID

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, func, select
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import OrderingList, ordering_list
from sqlalchemy.orm import column_property, relationship
from sqlalchemy_utils import PasswordType, force_auto_coercion

from nu.db.base_class import Base

if TYPE_CHECKING:
    from nu.models.channel import Channel, ChannelCharacter
    from nu.models.map import Room

force_auto_coercion()

__all__ = ["Player", "Character", "PlayerWindow", "PlayerWindowSetting"]

character_known_room = Table(
    "character_known_room",
    Base.metadata,
    Column("character_id", ForeignKey("character.id"), primary_key=True),
    Column("room_id", ForeignKey("room.id"), primary_key=True),
)


class Player(Base):
    username = Column(String)
    password: str = Column(PasswordType(schemes=["pbkdf2_sha512"]))
    email = Column(String)
    characters: list["Character"] = relationship("Character", back_populates="player")
    windows: OrderingList["PlayerWindow"] = relationship(
        "PlayerWindow",
        back_populates="player",
        uselist=True,
        order_by="PlayerWindow.position",
        collection_class=ordering_list("position"),
    )
    admin: bool


class Character(Base):
    name: str = Column(String, nullable=False)
    base_color = Column(String)
    player_id: PythonUUID = Column(ForeignKey("player.id"))
    player: Player = relationship("Player", back_populates="characters", uselist=False)
    admin = Column(Boolean, default=False)

    known_rooms: list[Room] = relationship(
        "Room", uselist=True, secondary=character_known_room
    )

    current_room_id: PythonUUID = Column(ForeignKey("room.id"))
    current_room: Room = relationship(
        "Room", back_populates="characters", uselist=False
    )

    character_channels: list["ChannelCharacter"] = relationship(
        "ChannelCharacter", back_populates="character", uselist=True
    )
    channels: list["Channel"] = association_proxy("character_channels", "channel")


Player.admin = column_property(
    select(func.bool_or(Character.admin))
    .where(Character.player_id == Player.id)
    .scalar_subquery()
)  # type: ignore


class PlayerWindowSetting(Base):
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

    window_id: PythonUUID = Column(ForeignKey("player_window.id"))
    window: "PlayerWindow" = relationship("PlayerWindow", back_populates="settings")


class PlayerWindow(Base):
    name = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    top = Column(Integer)
    left = Column(Integer)
    position = Column(Integer)
    component = Column(String)

    player_id: PythonUUID = Column(ForeignKey("player.id"))
    player: Player = relationship("Player", back_populates="windows", uselist=False)

    character_id: PythonUUID = Column(ForeignKey("character.id"))
    character: Character = relationship("Character", uselist=False)

    settings: List[PlayerWindowSetting] = relationship(
        "PlayerWindowSetting", back_populates="window", cascade="all, delete-orphan"
    )
