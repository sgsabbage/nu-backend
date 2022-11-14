from typing import Optional
from uuid import UUID

import strawberry
from sqlalchemy import select

from nu.core.grid import models
from nu.core.player.models import Character
from nu.core.player.types import Character as CharacterType
from nu.info import NuInfo
from nu.types import BaseType, deferred_type


@deferred_type()
class Area(BaseType[models.Area]):
    id: strawberry.ID
    name: str

    @strawberry.field
    async def rooms(self, info: "NuInfo") -> list["Room"]:
        from nu.core.grid.loaders import RoomLoader

        return await info.context.loaders.get_loader(RoomLoader).by_area_id(
            self.model.id
        )


@deferred_type()
class Room(BaseType[models.Room]):
    id: strawberry.ID
    name: str
    description: str | None
    x: int
    y: int

    @strawberry.field
    async def area(self, info: "NuInfo") -> Optional[Area]:
        from nu.core.grid.loaders import AreaLoader

        return await info.context.loaders.get_loader(AreaLoader).by_id(
            self.model.area_id
        )

    @strawberry.field
    async def exits(self, info: "NuInfo") -> list["Exit"]:
        session = info.context.session
        result = await session.execute(
            select(models.Exit).filter(models.Exit.start_room_id == self.id)
        )
        return [Exit.from_orm(c) for c in result.scalars().all()]

    @strawberry.field
    async def characters(self, info: "NuInfo") -> list[CharacterType]:
        session = info.context.session
        result = await session.execute(
            select(Character).filter(Character.current_room_id == self.id)
        )
        return [CharacterType.from_orm(c) for c in result.scalars().all()]


@deferred_type()
class Exit(BaseType[models.Exit]):
    id: strawberry.ID
    name: str | None
    secret: bool

    @strawberry.field
    async def start_room(self, info: "NuInfo") -> Optional[Room]:
        from nu.core.grid.loaders import RoomLoader

        return await info.context.loaders.get_loader(RoomLoader).by_id(
            self.model.start_room_id
        )

    @strawberry.field
    async def end_room(self, info: "NuInfo") -> Optional[Room]:
        from nu.core.grid.loaders import RoomLoader

        return await info.context.loaders.get_loader(RoomLoader).by_id(
            self.model.end_room_id
        )


@strawberry.input
class UpdateRoomInput:
    id: UUID

    name: str | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    x: int | None = strawberry.UNSET
    y: int | None = strawberry.UNSET


@strawberry.type
class UpdateRoomResult:
    room: Room


@strawberry.input
class UpdateAreaInput:
    id: UUID

    name: str | None = strawberry.UNSET
    description: str | None = strawberry.UNSET


@strawberry.type
class UpdateAreaResult:
    area: Area


@strawberry.input
class MoveCharacterToRoomInput:
    character_id: UUID
    room_id: UUID


@strawberry.type
class MoveCharacterToRoomResult:
    character: CharacterType


@strawberry.input
class MoveCharacterThroughExitInput:
    character_id: UUID
    exit_id: UUID


@strawberry.type
class MoveCharacterThroughExitResult:
    character: CharacterType
