import strawberry

from nu.info import NuInfo

from . import types
from .loaders import ChannelLoader


async def get_channels(info: "NuInfo") -> list[types.Channel]:
    return await info.context.loaders.get_loader(ChannelLoader).all()


@strawberry.type
class Query:
    channels: list[types.Channel] = strawberry.field(
        resolver=get_channels,
        # directives=[HasPermission(permissions=[Permission.CHANNEL_CREATE])],
    )
