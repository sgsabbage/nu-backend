import re
from uuid import UUID as PythonUUID

from sqlalchemy import Column, ForeignKey, Integer, MetaData
from sqlalchemy.orm import as_declarative, declared_attr, relationship

from nu.core.player.models import Character
from nu.db.base_class import convention

metadata = MetaData(naming_convention=convention, schema="plugin_magic")


@as_declarative(metadata=metadata)
class Base:
    @declared_attr
    def __tablename__(cls) -> str:
        """Convert CamelCase class name to underscores_between_words
        table name."""
        name = cls.__name__
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class CharacterMagic(Base):
    character_id: PythonUUID = Column(ForeignKey(Character.id), primary_key=True)
    character: Character = relationship(
        Character, back_populates="magic", uselist=False
    )
    current_mp = Column(Integer)
    total_mp = Column(Integer)
