from newmu.db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, Integer, Boolean
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from uuid import UUID as PythonUUID

class Area(Base):
    name = Column(String)

    rooms = relationship("Room", back_populates="area")

class Room(Base):
    name = Column(String)

    area_id = Column(ForeignKey("area.id"))
    area = relationship("Area", back_populates="rooms")

    x = Column(Integer)
    y = Column(Integer)

    exits = relationship("Exit", foreign_keys="Exit.start_room_id", back_populates="start_room")

class Exit(Base):
    name = Column(String)
    secret = Column(Boolean, default=False)
    
    start_room_id = Column(ForeignKey("room.id"))
    start_room = relationship("Room", foreign_keys=start_room_id, back_populates="exits")
    end_room_id = Column(ForeignKey("room.id"))
    end_room = relationship("Room", foreign_keys=end_room_id)

