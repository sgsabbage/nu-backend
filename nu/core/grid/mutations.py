import strawberry
from sqlalchemy import text

from nu.core.player.loaders import CharacterLoader
from nu.core.player.types import Character as CharacterType
from nu.info import NuInfo

from .loaders import AreaLoader, RoomLoader
from .types import (
    Area,
    MoveCharacterThroughExitInput,
    MoveCharacterThroughExitResult,
    MoveCharacterToRoomInput,
    MoveCharacterToRoomResult,
    Room,
    UpdateAreaInput,
    UpdateAreaResult,
    UpdateRoomInput,
    UpdateRoomResult,
)


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def update_room(
        self, info: "NuInfo", input: UpdateRoomInput
    ) -> UpdateRoomResult:
        room = await info.context.loaders.get_loader(RoomLoader).by_id(input.id)

        assert room, "Room not found"

        room_model = room._model

        for f in ("name", "description", "x", "y"):
            if (val := getattr(input, f)) is not strawberry.UNSET:
                setattr(room_model, f, val)

        await info.context.session.execute(
            text(f"SELECT pg_notify('grid', 'room.{room_model.id}')")
        )

        return UpdateRoomResult(room=Room.from_orm(room_model))

    @strawberry.mutation
    async def update_area(
        self, info: "NuInfo", input: UpdateAreaInput
    ) -> UpdateAreaResult:
        area = await info.context.loaders.get_loader(AreaLoader).by_id(input.id)

        assert area, "Area not found"

        area_model = area._model

        for f in ("name", "description"):
            if (val := getattr(input, f)) is not strawberry.UNSET:
                setattr(area_model, f, val)

        await info.context.session.execute(
            text(f"SELECT pg_notify('grid', 'area.{area_model.id}')")
        )

        return UpdateAreaResult(area=Area.from_orm(area_model))

    @strawberry.mutation
    async def move_character_to_room(
        self, info: "NuInfo", input: MoveCharacterToRoomInput
    ) -> MoveCharacterToRoomResult:
        character = await info.context.loaders.get_loader(CharacterLoader).by_id(
            input.character_id
        )
        room = await info.context.loaders.get_loader(RoomLoader).by_id(input.room_id)
        assert character, "Character not found"
        assert room, "Room not found"

        character._model.current_room = room._model
        await info.context.session.flush()
        return MoveCharacterToRoomResult(
            character=CharacterType.from_orm(character._model)
        )

    @strawberry.mutation
    async def move_character_through_exit(
        self, info: "NuInfo", input: MoveCharacterThroughExitInput
    ) -> MoveCharacterThroughExitResult:
        character = await info.context.loaders.get_loader(CharacterLoader).by_id(
            input.character_id
        )

        # TODO: Validate character knows this exit exists
        assert character, "Character not found"

        return MoveCharacterThroughExitResult(
            character=CharacterType.from_orm(character._model)
        )
