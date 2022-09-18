from typing import TYPE_CHECKING

import strawberry
from sqlalchemy import select

import nu.graphql.types as types
import nu.models as models
from nu.graphql.directives import HasPermission
from nu.models.player import Permission

if TYPE_CHECKING:
    from nu.main import NuInfo


async def get_current_player(info: "NuInfo") -> types.Player:
    session = info.context.session
    result = await session.execute(
        select(models.Player).where(models.Player.id == info.context.player.id)
    )
    return types.Player.from_orm(result.scalar_one())


async def get_channels(info: "NuInfo") -> list[types.Channel]:
    session = info.context.session
    result = await session.execute(select(models.Channel))
    return [types.Channel.from_orm(r) for r in result.scalars().all()]


@strawberry.type
class Query:

    me: types.Player = strawberry.field(resolver=get_current_player)

    @strawberry.field
    async def areas(self, info: "NuInfo") -> list[types.Area]:
        session = info.context.session
        result = await session.execute(select(models.Area))
        return [types.Area.from_orm(a) for a in result.scalars().all()]

    @strawberry.field
    async def rooms(self, info: "NuInfo") -> list[types.Room]:
        return await info.context.loaders.rooms.all()

    channels: list[types.Channel] = strawberry.field(
        resolver=get_channels,
        directives=[HasPermission(permissions=[Permission.CHANNEL_CREATE])],
    )

    # @strawberry.field
    # async def channel(self, info: "NuInfo", id: strawberry.ID) -> types.Channel:
    #     c = await info.context.loaders.channels.by_id(UUID(id))
    #     return types.Channel.from_orm(c) if c else None

    @strawberry.field
    async def windows(self, info: "NuInfo") -> list[types.Window]:
        result = await info.context.session.execute(
            select(models.PlayerWindow)
            .where(models.PlayerWindow.player_id == info.context.player.id)
            .order_by(models.PlayerWindow.position)
        )
        return [types.Window.from_orm(w) for w in result.scalars().all()]
