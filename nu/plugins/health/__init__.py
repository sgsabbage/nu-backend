from math import e
from typing import Protocol, runtime_checkable
from uuid import UUID as PythonUUID

import strawberry
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

import nu.core.player.types as coretypes
from nu.core.player.models import Character as CharacterModel
from nu.db.base_class import Base


class CharacterHealthModel(Base):
    character_id: PythonUUID = Column(ForeignKey("character.id"), primary_key=True)
    character: CharacterModel = relationship(
        "Character", back_populates="health", uselist=False
    )
    hp = Column(Integer)


@runtime_checkable
class HasHealth(Protocol):
    health: CharacterHealthModel


setattr(
    CharacterModel,
    "health",
    relationship(
        "CharacterHealthModel",
        back_populates="character",
        lazy="selectin",
        uselist=False,
    ),
)


def get_hp(root: coretypes.Character) -> int:
    assert isinstance(root._model, HasHealth)
    if root._model.health:
        return root._model.health.hp or 0
    return 0


setattr(
    coretypes.Character,
    "health",
    strawberry.field(resolver=get_hp),
)
