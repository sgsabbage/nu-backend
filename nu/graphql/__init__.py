from typing import TYPE_CHECKING, Any, Awaitable, Union

from strawberry.field import StrawberryField

from nu.graphql.directives import ResolvableDirective

if TYPE_CHECKING:
    from nu.info import NuInfo


def get_result(
    self: StrawberryField,
    source: Any,
    info: "NuInfo",
    args: list[Any],
    kwargs: dict[str, Any],
) -> Union[Awaitable[Any], Any]:
    for directive in [
        d for d in info._field.directives if isinstance(d, ResolvableDirective)
    ]:
        directive.resolve(source, info, args, kwargs)

    if self.base_resolver:
        return self.base_resolver(*args, **kwargs)

    return self.default_resolver(source, self.python_name)
