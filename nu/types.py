import dataclasses
from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol, Type, TypeVar

import strawberry

if TYPE_CHECKING:
    from nu.db.base_class import Base


T = TypeVar("T")
C = TypeVar("C", bound="BaseType")  # type: ignore


class HasModel(Protocol):
    model: "Base"


class BaseType(
    Generic[T],
):
    model: strawberry.Private[T]

    @classmethod
    def from_orm(cls: type[C], instance: T) -> C:
        attrs = {}
        for field in [f for f in dataclasses.fields(cls) if f.init]:
            attrs[field.name] = getattr(instance, field.name)
        obj = cls(**attrs)
        obj.model = instance
        return obj

    @classmethod
    def add_extra_field(cls, name: str, resolver: Callable[..., Any]) -> None:
        setattr(cls, name, strawberry.field(resolver=resolver))


types_to_resolve: list[tuple[Type[Any], str | None]] = []


def deferred_type(name: str | None = None) -> Callable[[Type[C]], Type[C]]:
    def wrap(cls: Type[C]) -> Type[C]:
        types_to_resolve.append((cls, name))
        return cls

    return wrap


def resolve_types() -> None:
    for t in types_to_resolve:
        strawberry.type(t[0], name=t[1])
