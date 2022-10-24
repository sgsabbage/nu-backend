from typing import TYPE_CHECKING, Annotated, Optional

import strawberry
from sqlalchemy import select

from nu.core.player.models import Character as CharacterModel
from nu.info import NuInfo
from nu.types import BaseType, deferred_type

from . import models

if TYPE_CHECKING:
    from nu.core.grid.types import Room


@deferred_type
class Player(BaseType[models.Player]):
    id: strawberry.ID
    username: str
    email: str

    @strawberry.type(name="PlayerPlugins")
    class Plugins:
        count: int = 0

    @strawberry.field
    async def plugins(self) -> Plugins:
        return self.Plugins()

    @strawberry.field
    async def characters(self, info: "NuInfo") -> list["Character"]:
        from nu.core.player.loaders import CharacterLoader

        return await info.context.loaders.get_loader(CharacterLoader).by_player(
            self._model
        )

    @strawberry.field
    async def windows(self, info: "NuInfo") -> list["Window"]:
        session = info.context.session
        result = await session.execute(
            select(models.PlayerWindow)
            .where(models.PlayerWindow.player_id == self.id)
            .order_by(models.PlayerWindow.position)
        )
        return [Window.from_orm(w) for w in result.scalars().all()]


@deferred_type
class Character(BaseType[CharacterModel]):
    id: strawberry.ID
    name: str
    base_color: str | None

    @strawberry.field
    async def player(self, info: "NuInfo") -> Optional["Player"]:
        from nu.core.player.loaders import PlayerLoader

        return await info.context.loaders.get_loader(PlayerLoader).by_id(
            self._model.player_id
        )

    @strawberry.field
    async def current_room(
        self, info: "NuInfo"
    ) -> Optional[Annotated["Room", strawberry.lazy("nu.core.grid.types")]]:
        from nu.core.grid.loaders import RoomLoader

        return await info.context.loaders.get_loader(RoomLoader).by_id(
            self._model.current_room_id
        )


@deferred_type
class WindowSetting(BaseType[models.PlayerWindowSetting]):
    key: str
    value: str


@deferred_type
class Window(BaseType[models.PlayerWindow]):
    id: strawberry.ID
    name: str
    component: str | None
    width: int
    height: int
    top: int
    left: int

    @strawberry.field
    async def character(self, info: "NuInfo") -> Character | None:
        from nu.core.player.loaders import CharacterLoader

        return await info.context.loaders.get_loader(CharacterLoader).by_id(
            self._model.character_id
        )

    @strawberry.field
    async def settings(self, info: "NuInfo") -> list[WindowSetting]:
        session = info.context.session
        result = await session.execute(
            select(models.PlayerWindowSetting)
            .join(models.PlayerWindowSetting.window)
            .where(models.PlayerWindow.id == self.id)
        )
        return [WindowSetting.from_orm(c) for c in result.scalars().all()]
