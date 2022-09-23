from typing import AsyncGenerator
from uuid import UUID

import strawberry
from broadcaster import Event
from sqlalchemy.ext.asyncio import AsyncSession

from nu.core.grid.loaders import AreaLoader, RoomLoader
from nu.info import NuInfo
from nu.subscriptions import subscribe

from .types import Area as AreaType
from .types import Room as RoomType


async def sub_grid_status(
    event: Event, session: AsyncSession, info: "NuInfo"
) -> RoomType | AreaType | None:
    type, id = event.message.split(".")

    object_id = UUID(id)
    if type == "room":
        return await info.context.loaders.get_loader(RoomLoader).by_id(object_id)
    elif type == "area":
        return await info.context.loaders.get_loader(AreaLoader).by_id(object_id)
    return None


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def grid(
        self, info: "NuInfo"
    ) -> AsyncGenerator[RoomType | AreaType | None, None]:
        return subscribe("grid", info, sub_grid_status)
