import dataclasses
from typing import TYPE_CHECKING, Any, Generic, Type, TypeVar

import strawberry

if TYPE_CHECKING:
    from nu.db.base_class import Base


T = TypeVar("T", bound="Base")
C = TypeVar("C", bound="BaseType")  # type: ignore


class BaseType(
    Generic[T],
):
    _model: T

    @classmethod
    def from_orm(cls: type[C], instance: T) -> C:
        attrs = {}
        for field in [f for f in dataclasses.fields(cls) if f.init]:
            attrs[field.name] = getattr(instance, field.name)
        obj = cls(**attrs)
        obj._model = instance
        return obj


types_to_resolve: list[Any] = []


def deferred_type(cls: Type[C]) -> Type[C]:
    types_to_resolve.append(cls)
    return cls


def resolve_types() -> None:
    for t in types_to_resolve:
        strawberry.type(t)
