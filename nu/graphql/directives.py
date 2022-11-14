from abc import ABC
from typing import TYPE_CHECKING, Any

import strawberry
from strawberry.schema_directive import Location

from nu.core.models import Permission

if TYPE_CHECKING:
    from nu.info import NuInfo


class ResolvableDirective(ABC):
    def resolve(
        self, source: Any, info: "NuInfo", args: list[Any], kwargs: dict[str, Any]
    ) -> None:
        ...


@strawberry.schema_directive(locations=[Location.FIELD_DEFINITION])
class HasPermission(ResolvableDirective):
    permissions: list[Permission]

    def resolve(
        self, source: Any, info: "NuInfo", args: list[Any], kwargs: dict[str, Any]
    ) -> None:
        player = info.context.player
        if not player:
            raise Exception("Not logged in")
        return
        # for permission in self.permissions:
        #     print(player.permissions)
        #     print(type(player.permissions[0]))
        #     if permission not in player.permissions:
        #         raise Exception(f"Missing permission {permission}")
