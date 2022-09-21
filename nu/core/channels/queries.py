import strawberry
from sqlalchemy import select

from nu.core.player.models import Permission
from nu.graphql.directives import HasPermission
from nu.info import NuInfo

from . import models, types


async def get_channels(info: "NuInfo") -> list[types.Channel]:
    session = info.context.session
    result = await session.execute(select(models.Channel))
    return [types.Channel.from_orm(r) for r in result.scalars().all()]


@strawberry.type
class Query:
    channels: list[types.Channel] = strawberry.field(
        resolver=get_channels,
        # directives=[HasPermission(permissions=[Permission.CHANNEL_CREATE])],
    )
