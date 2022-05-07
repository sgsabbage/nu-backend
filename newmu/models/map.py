from uuid import UUID as PythonUUID

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from newmu.db.base_class import Base


class Area(Base):
    name = Column(String)

    rooms: list["Room"] = relationship("Room", back_populates="area", uselist=True)


class Room(Base):
    name = Column(String)

    area_id: PythonUUID = Column(ForeignKey("area.id"))
    area: Area = relationship("Area", back_populates="rooms", uselist=False)

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
