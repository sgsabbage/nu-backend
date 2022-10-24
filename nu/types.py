import dataclasses
from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol, Type, TypeVar

import strawberry
from strawberry.annotation import StrawberryAnnotation
from strawberry.field import StrawberryField
from strawberry.tools import merge_types
from strawberry.types.fields.resolver import StrawberryResolver

if TYPE_CHECKING:
    from nu.db.base_class import Base


T = TypeVar("T", bound="Base")
C = TypeVar("C", bound="BaseType")  # type: ignore


class HasModel(Protocol):
    model: "Base"


class BaseType(
    Generic[T],
):
    _model: strawberry.Private[T]
    _extra_fields: strawberry.Private[dict[str, Any]]

    @classmethod
    def from_orm(cls: type[C], instance: T) -> C:
        attrs = {}
        for field in [f for f in dataclasses.fields(cls) if f.init]:
            attrs[field.name] = getattr(instance, field.name)
        obj = cls(**attrs)
        obj._model = instance
        return obj

    @classmethod
    def add_extra_field(cls, name: str, resolver: Callable[..., Any]) -> None:
        if not hasattr(cls, "_extra_fields"):
            cls._extra_fields = {}
        cls._extra_fields[name] = strawberry.field(resolver=resolver)

    @classmethod
    def generate_extra_class(cls: type[C]) -> None:
        if not hasattr(cls, "_extra_fields"):
            return

        @strawberry.type
        class Extras:
            model: strawberry.Private[T]

        ClassExtras = strawberry.type(
            type(f"{cls.__name__}Extras", (), cls._extra_fields)
        )

        ClassExtras = merge_types(f"{cls.__name__}Extras", (Extras, ClassExtras))

        def get_extras(self: C) -> Any:
            return ClassExtras(model=self._model)

        setattr(
            cls,
            "extras",
            StrawberryField(
                type_annotation=StrawberryAnnotation(ClassExtras),
                base_resolver=StrawberryResolver(get_extras, type_override=ClassExtras),
            ),
        )


types_to_resolve: list[tuple[Type[Any], str | None]] = []


def deferred_type(name: str | None = None) -> Callable[[Type[Any]], Type[Any]]:
    def wrap(cls: Type[Any]) -> Type[Any]:
        types_to_resolve.append((cls, name))
        return cls

    return wrap


def resolve_types() -> None:
    for t in types_to_resolve:
        t[0].generate_extra_class()
        strawberry.type(t[0], name=t[1])
