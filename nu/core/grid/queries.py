import strawberry

from nu.core.grid.loaders import AreaLoader, RoomLoader
from nu.info import NuInfo

from .types import Area as AreaType
from .types import Room as RoomType


async def get_rooms(info: "NuInfo") -> list[RoomType]:
    return await info.context.loaders.get_loader(RoomLoader).all()


async def get_areas(info: "NuInfo") -> list[AreaType]:
    return await info.context.loaders.get_loader(AreaLoader).all()


@strawberry.type
class Query:
    areas: list[AreaType] = strawberry.field(resolver=get_areas)
    rooms: list[RoomType] = strawberry.field(resolver=get_rooms)
