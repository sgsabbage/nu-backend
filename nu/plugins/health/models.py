from uuid import UUID as PythonUUID

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from nu.core.player.models import Character as CharacterModel
from nu.db.base_class import Base


class CharacterHealth(Base):
    character_id: PythonUUID = Column(ForeignKey("character.id"), primary_key=True)
    character: CharacterModel = relationship(
        "Character", back_populates="health", uselist=False
    )
    current_hp = Column(Integer)
    total_hp = Column(Integer)
