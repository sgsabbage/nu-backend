import strawberry

from nu.info import NuInfo

from .types import Area as AreaType
from .types import Room as RoomType


async def get_rooms(info: "NuInfo") -> list[RoomType]:
    return await info.context.loaders.rooms.all()


async def get_areas(info: "NuInfo") -> list[AreaType]:
    return await info.context.loaders.areas.all()


@strawberry.type
class Query:
    areas: list[AreaType] = strawberry.field(resolver=get_areas)
    rooms: list[RoomType] = strawberry.field(resolver=get_rooms)
