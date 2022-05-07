from typing import TYPE_CHECKING, List
from uuid import UUID as PythonUUID

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy_utils import PasswordType, force_auto_coercion

from newmu.db.base_class import Base

if TYPE_CHECKING:
    from newmu.models.channel import Channel, ChannelCharacter

force_auto_coercion()

__all__ = ["Player", "Character", "PlayerWindow", "PlayerWindowSetting"]


class Player(Base):
    username = Column(String)
    password: str = Column(PasswordType(schemes=["pbkdf2_sha512"]))
    email = Column(String)
    characters: list["Character"] = relationship("Character", back_populates="player")
    windows: list["PlayerWindow"] = relationship(
        "PlayerWindow", back_populates="player", uselist=True
    )


class Character(Base):
    name: str = Column(String, nullable=False)
    base_color = Column(String)
    player_id: PythonUUID = Column(ForeignKey("player.id"))
    player: Player = relationship("Player", back_populates="characters", uselist=False)

    character_channels: list["ChannelCharacter"] = relationship(
        "ChannelCharacter", back_populates="character", uselist=True
    )
    channels: list["Channel"] = association_proxy("character_channels", "channel")


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
    z = Column(Integer)
    component = Column(String)

    player_id: PythonUUID = Column(ForeignKey("player.id"))
    player: Player = relationship("Player", back_populates="windows", uselist=False)

    character_id: PythonUUID = Column(ForeignKey("character.id"))
    character: Character = relationship("Character", uselist=False)

    settings: List[PlayerWindowSetting] = relationship(
        "PlayerWindowSetting", back_populates="window", cascade="all, delete-orphan"
    )
