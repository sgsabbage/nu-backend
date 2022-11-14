import re
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar
from uuid import UUID as PythonUUID

from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    declared_attr,
    mapped_column,
)
from sqlalchemy.sql.expression import text
from typing_extensions import Annotated

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention, schema="core")

pkuuid = Annotated[
    PythonUUID,
    mapped_column(
        UUID(as_uuid=True),
        server_default=text("uuid_generate_v4()"),
        primary_key=True,
        init=False,
    ),
]


class BaseMixin:
    if TYPE_CHECKING:
        __name__: ClassVar[str]

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Convert CamelCase class name to underscores_between_words
        table name."""
        name = cls.__name__
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


class Base(MappedAsDataclass, DeclarativeBase, BaseMixin):
    metadata = metadata


class AutoName(Enum):
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[Any]
    ) -> str:
        return name
