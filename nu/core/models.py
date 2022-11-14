from enum import auto
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.ext.orderinglist import OrderingList, ordering_list
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import PasswordType, force_auto_coercion

from nu.db.base_class import AutoName, Base, pkuuid

force_auto_coercion()

__all__ = [
    "Player",
    "Character",
    "Permission",
    "PlayerWindow",
    "PlayerWindowSetting",
]


class Permission(AutoName):
    CHANNEL_CREATE = auto()
    CHANNEL_UPDATE = auto()
    CHANNEL_DELETE = auto()


# class Role(Base):
#     id: Mapped[pkuuid]
#     name: Mapped[str]
#     permissions: Mapped[list[Permission]]


class Player(Base):
    id: Mapped[pkuuid]
    username: Mapped[str]
    email: Mapped[str]
    password: Mapped[str] = mapped_column(PasswordType(schemes=["pbkdf2_sha512"]))
    # permissions: Mapped[list["Permission"]]
    characters: Mapped[list["Character"]] = relationship(
        back_populates="player", default_factory=list
    )
    windows: Mapped[OrderingList["PlayerWindow"]] = relationship(
        back_populates="player",
        order_by="PlayerWindow.position",
        collection_class=ordering_list("position"),
        default_factory=list,
    )
    # roles: Mapped[list["Role"]] = relationship(uselist=True, secondary=player_role)


class Character(Base):
    id: Mapped[pkuuid]
    name: Mapped[str]
    player: Mapped[Player] = relationship(back_populates="characters")
    base_color: Mapped[Optional[str]] = mapped_column(default=None)
    player_id: Mapped[UUID] = mapped_column(
        ForeignKey("player.id"), default=None, nullable=False
    )


class PlayerWindowSetting(Base):
    id: Mapped[pkuuid]
    key: Mapped[str]
    value: Mapped[str]

    window_id: Mapped[UUID] = mapped_column(ForeignKey("player_window.id"))
    window: Mapped["PlayerWindow"] = relationship(back_populates="settings")


class PlayerWindow(Base):
    id: Mapped[pkuuid]
    name: Mapped[str]
    width: Mapped[int]
    height: Mapped[int]
    top: Mapped[int]
    left: Mapped[int]
    position: Mapped[int]
    component: Mapped[str]

    player: Mapped[Player] = relationship(back_populates="windows")
    character: Mapped[Character] = relationship()

    player_id: Mapped[UUID] = mapped_column(ForeignKey("player.id"), default=None)
    character_id: Mapped[UUID] = mapped_column(ForeignKey("character.id"), default=None)

    settings: Mapped[list[PlayerWindowSetting]] = relationship(
        back_populates="window", cascade="all, delete-orphan", default_factory=list
    )
