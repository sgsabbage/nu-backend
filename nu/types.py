import dataclasses
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from nu.db.base_class import Base


T = TypeVar("T", bound="Base")
C = TypeVar("C", bound="BaseType")  # type: ignore


class BaseType(Generic[T]):
    _model: T

    @classmethod
    def from_orm(cls: type[C], instance: T) -> C:
        attrs = {}
        for field in [f for f in dataclasses.fields(cls) if f.init]:
            attrs[field.name] = getattr(instance, field.name)
        obj = cls(**attrs)
        obj._model = instance
        return obj
