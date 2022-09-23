import strawberry

from nu.core.channels.loaders import ChannelLoader
from nu.core.player.models import Permission
from nu.graphql.directives import HasPermission
from nu.info import NuInfo

from . import types


async def get_channels(info: "NuInfo") -> list[types.Channel]:
    return await info.context.loaders.get_loader(ChannelLoader).all()


@strawberry.type
class Query:
    channels: list[types.Channel] = strawberry.field(
        resolver=get_channels,
        # directives=[HasPermission(permissions=[Permission.CHANNEL_CREATE])],
    )
