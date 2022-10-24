import strawberry

import nu.core.player.types as coretypes
from nu.info import NuInfo


def get_mp() -> int:
    return 20


setattr(
    coretypes.Character,
    "magic",
    strawberry.field(resolver=get_mp),
)
