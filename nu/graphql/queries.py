from typing import TYPE_CHECKING
from uuid import UUID

import strawberry
from sqlalchemy import select

import nu.graphql.types as types
import nu.models as models

if TYPE_CHECKING:
    from nu.main import NuInfo


async def get_current_player(info: "NuInfo") -> types.Player:
    session = info.context.session
    result = await session.execute(
        select(models.Player).where(models.Player.id == info.context.player.id)
    )
    return types.Player.from_orm(result.scalar_one())


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
        session = info.context.session
        result = await session.execute(select(models.Room))
        return [types.Room.from_orm(r) for r in result.scalars().all()]

    @strawberry.field
    async def channels(self, info: "NuInfo") -> list[types.Channel]:
        session = info.context.session
        result = await session.execute(select(models.Channel))
        return [types.Channel.from_orm(r) for r in result.scalars().all()]

    @strawberry.field
    async def channel(self, info: "NuInfo", id: strawberry.ID) -> types.Channel:
        c = await info.context.loaders.channels.load(UUID(id))
        return types.Channel.from_orm(c)
