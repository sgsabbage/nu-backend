from enum import auto
from typing import TYPE_CHECKING
from uuid import UUID as PythonUUID

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from nu.db.base_class import AutoName, Base

if TYPE_CHECKING:
    from nu.core.player.models import Character

__all__ = ["Area", "Room", "RoomStatus", "Exit"]


class Area(Base):
    name = Column(String)

    rooms: list["Room"] = relationship("Room", back_populates="area", uselist=True)


class RoomStatus(AutoName):
    PRIVATE = auto()
    SECRET = auto()
    PUBLIC = auto()


class Room(Base):
    name = Column(String)
    description = Column(String)

    area_id: PythonUUID = Column(ForeignKey("area.id"))
    area: Area = relationship("Area", back_populates="rooms", uselist=False)

    status = Column(Enum(RoomStatus), default=RoomStatus.PRIVATE)

    characters: list["Character"] = relationship(
        "Character", back_populates="current_room", uselist=True
    )

    x = Column(Integer)
    y = Column(Integer)

    exits: list["Exit"] = relationship(
        "Exit",
        foreign_keys="Exit.start_room_id",
        back_populates="start_room",
        uselist=True,
    )


class Exit(Base):
    name = Column(String)
    secret = Column(Boolean, default=False)

    start_room_id: PythonUUID = Column(ForeignKey("room.id"))
    start_room: Room = relationship(
        "Room", foreign_keys=start_room_id, back_populates="exits", uselist=False
    )
    end_room_id: PythonUUID = Column(ForeignKey("room.id"))
    end_room: Room = relationship("Room", foreign_keys=end_room_id, uselist=False)
