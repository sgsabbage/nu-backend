from typing import Optional

import strawberry
from sqlalchemy import select

import nu
from nu.core import models
from nu.core.models import Character as CharacterModel
from nu.info import NuInfo
from nu.types import BaseType


@nu.type()
class Player(BaseType[models.Player]):
    id: strawberry.ID
    username: str
    email: str

    @strawberry.field
    async def characters(self, info: "NuInfo") -> list["Character"]:
        from nu.core.loaders import CharacterLoader

        return await info.context.loaders.get_loader(CharacterLoader).by_player(
            self.model
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


@nu.type()
class Character(BaseType[CharacterModel]):
    id: strawberry.ID
    name: str
    base_color: str | None

    @strawberry.field
    async def player(self, info: "NuInfo") -> Optional["Player"]:
        from nu.core.loaders import PlayerLoader

        return await info.context.loaders.get_loader(PlayerLoader).by_id(
            self.model.player_id
        )


@nu.type()
class WindowSetting(BaseType[models.PlayerWindowSetting]):
    key: str
    value: str


@nu.type()
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
        from nu.core.loaders import CharacterLoader

        return await info.context.loaders.get_loader(CharacterLoader).by_id(
            self.model.character_id
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
