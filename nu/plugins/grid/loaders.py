import asyncio
from typing import Any
from uuid import UUID

from sqlalchemy import select

from nu.loaders import BaseLoader

from .models import Area, Room
from .types import Area as AreaType
from .types import Room as RoomType


class AreaLoader(BaseLoader[Area, AreaType]):
    model = Area
    type = AreaType

    async def can_see(self, obj: Area) -> bool:
        return True


class RoomLoader(BaseLoader[Room, RoomType]):
    model = Room
    type = RoomType

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._room_lock = asyncio.Lock()
        self._room_done = False
        self._known_rooms: list[Room] = []

    async def by_area_id(self, area_id: UUID) -> list[RoomType]:
        result = await self.session.execute(select(Room).where(Room.area_id == area_id))
        rooms = result.scalars().all()

        self.loader.prime_many({r.id: r for r in rooms})

        return [RoomType.from_orm(r) for r in rooms if await self.can_see(r)]

    async def can_see(self, obj: Room) -> bool:
        if obj not in await self.known_rooms:
            return False
        return True

    @property
    async def known_rooms(self) -> list[Room]:
        async with self._room_lock:
            if not self._room_done:
                # TODO: Tie this back to the correct known rooms list
                self._known_rooms = (
                    (await self.session.execute(select(Room))).scalars().all()
                )
                self._room_done = True
            return self._known_rooms
