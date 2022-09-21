from typing import TYPE_CHECKING, Annotated, Optional

import strawberry
from sqlalchemy import select

from nu.core.player.models import Character as CharacterModel
from nu.info import NuInfo
from nu.types import BaseType

from . import models

if TYPE_CHECKING:
    from nu.core.grid.types import Room


@strawberry.type
class Player(BaseType[models.Player]):
    id: strawberry.ID
    username: str
    email: str

    @strawberry.field
    async def characters(self, info: "NuInfo") -> list["Character"]:
        return await info.context.loaders.characters.by_player(self._model)

    @strawberry.field
    async def windows(self, info: "NuInfo") -> list["Window"]:
        session = info.context.session
        result = await session.execute(
            select(models.PlayerWindow)
            .where(models.PlayerWindow.player_id == self.id)
            .order_by(models.PlayerWindow.position)
        )
        return [Window.from_orm(w) for w in result.scalars().all()]


@strawberry.type
class Character(BaseType[CharacterModel]):
    id: strawberry.ID
    name: str
    base_color: str | None

    @strawberry.field
    async def player(self, info: "NuInfo") -> Optional["Player"]:
        return await info.context.loaders.players.by_id(self._model.player_id)

    @strawberry.field
    async def current_room(
        self, info: "NuInfo"
    ) -> Optional[Annotated["Room", strawberry.lazy("nu.core.grid.types")]]:
        return await info.context.loaders.rooms.by_id(self._model.current_room_id)


@strawberry.type
class WindowSetting(BaseType[models.PlayerWindowSetting]):
    key: str
    value: str


@strawberry.type
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
        return await info.context.loaders.characters.by_id(self._model.character_id)

    @strawberry.field
    async def settings(self, info: "NuInfo") -> list[WindowSetting]:
        session = info.context.session
        result = await session.execute(
            select(models.PlayerWindowSetting)
            .join(models.PlayerWindowSetting.window)
            .where(models.PlayerWindow.id == self.id)
        )
        return [WindowSetting.from_orm(c) for c in result.scalars().all()]
