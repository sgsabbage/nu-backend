from __future__ import annotations

import dataclasses
import datetime
from typing import TYPE_CHECKING, Generic, Optional, TypeVar
from uuid import UUID

import strawberry
from dateutil import parser
from graphql import GraphQLError
from sqlalchemy import desc, func, select

import nu.models as models

from .pagination import Connection, Edge, PageInfo

if TYPE_CHECKING:
    from nu.db.base_class import Base
    from nu.main import NuInfo


T = TypeVar("T", bound="Base")
C = TypeVar("C", bound="BaseType")  # type: ignore


class BaseType(Generic[T]):
    _model: T

    @classmethod
    def from_orm(cls: type[C], instance: T) -> C:
        attrs = {}
        for field in [f for f in dataclasses.fields(cls) if f.init]:
            attrs[field.name] = getattr(instance, field.name)
        obj = cls(**attrs)
        obj._model = instance
        return obj


@strawberry.type
class Player(BaseType[models.Player]):
    id: strawberry.ID
    username: str
    email: str
    admin: bool

    @strawberry.field
    async def characters(self, info: "NuInfo") -> list["Character"]:
        session = info.context.session
        result = await session.execute(
            select(models.Character).filter(models.Character.player_id == self.id)
        )
        return [Character.from_orm(c) for c in result.scalars().all()]

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
class Character(BaseType[models.Character]):
    id: strawberry.ID
    name: str
    base_color: str | None

    @strawberry.field
    async def current_room(self, info: "NuInfo") -> Optional[Room]:
        return await info.context.loaders.rooms.by_id(self._model.current_room_id)


@strawberry.type
class Area(BaseType[models.Area]):
    id: strawberry.ID
    name: str

    @strawberry.field
    async def rooms(self, info: "NuInfo") -> list[Room]:
        return await info.context.loaders.rooms.by_area(self._model)


@strawberry.type
class Room(BaseType[models.Room]):
    id: strawberry.ID
    name: str
    description: str | None
    x: int
    y: int

    @strawberry.field
    async def exits(self, info: "NuInfo") -> list[Exit]:
        session = info.context.session
        result = await session.execute(
            select(models.Exit).filter(models.Exit.start_room_id == self.id)
        )
        return [Exit.from_orm(c) for c in result.scalars().all()]

    @strawberry.field
    async def area(self, info: "NuInfo") -> Area:
        return Area.from_orm(await info.context.loaders.areas.load(self._model.area_id))

    @strawberry.field
    async def characters(self, info: "NuInfo") -> list[Character]:
        session = info.context.session
        result = await session.execute(
            select(models.Character).filter(models.Character.current_room_id == self.id)
        )
        return [Character.from_orm(c) for c in result.scalars().all()]


@strawberry.type
class Exit(BaseType[models.Exit]):
    id: UUID
    name: str | None
    secret: bool

    @strawberry.field
    async def start_room(self, info: "NuInfo") -> Optional[Room]:
        return await info.context.loaders.rooms.by_id(self._model.start_room_id)

    @strawberry.field
    async def end_room(self, info: "NuInfo") -> Optional[Room]:
        return await info.context.loaders.rooms.by_id(self._model.end_room_id)


@strawberry.type
class ChannelMessage(BaseType[models.ChannelMessage]):
    id: strawberry.ID
    timestamp: datetime.datetime
    message: str

    @strawberry.field
    async def character(self, info: "NuInfo") -> Optional[Character]:
        return await info.context.loaders.characters.by_id(self._model.character_id)

    @strawberry.field
    async def channel(self, info: "NuInfo") -> Channel:
        return Channel.from_orm(
            await info.context.loaders.channels.load(self._model.channel_id)
        )


@strawberry.type
class Channel(BaseType[models.Channel]):
    id: strawberry.ID
    name: str
    description: str | None

    @strawberry.field
    async def messages(
        self,
        info: "NuInfo",
        first: int | None = None,
        last: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Connection[ChannelMessage]:
        if first is not None and last is not None:
            raise GraphQLError("Cannot specify first and last")
        session = info.context.session

        stmt = select(models.ChannelMessage).filter(
            models.ChannelMessage.channel_id == self.id
        )

        bounds_stmnt = select(
            func.min(models.ChannelMessage.timestamp),
            func.max(models.ChannelMessage.timestamp),
        ).where(models.ChannelMessage.channel_id == self.id)
        bounds = (await session.execute(bounds_stmnt)).first()

        if after is not None:
            stmt = stmt.where(models.ChannelMessage.timestamp > parser.isoparse(after))
        if before is not None:
            stmt = stmt.where(models.ChannelMessage.timestamp < parser.isoparse(before))

        if last is None:
            stmt = stmt.order_by(models.ChannelMessage.timestamp)
        else:
            stmt = stmt.order_by(desc(models.ChannelMessage.timestamp)).limit(last)

        if first is not None:
            stmt = stmt.limit(first)

        result = await session.execute(stmt)
        results: list[models.ChannelMessage] = result.scalars().all()

        if last:
            results.reverse()

        has_next_page = False
        has_previous_page = False

        if bounds is None or bounds[0] is None:
            pass
        elif results:
            has_next_page = bounds[1] > results[-1].timestamp
            has_previous_page = bounds[0] < results[0].timestamp
        elif before is not None:
            has_next_page = True
        elif after is not None:
            has_previous_page = True

        pi = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=has_previous_page,
            start_cursor=None,
            end_cursor=None,
        )
        if results:
            pi.start_cursor = results[0].timestamp.isoformat()
            pi.end_cursor = results[-1].timestamp.isoformat()

        return Connection[ChannelMessage](
            page_info=pi,
            edges=[
                Edge[ChannelMessage](
                    cursor=r.timestamp.isoformat(), node=ChannelMessage.from_orm(r)
                )
                for r in results
            ],
        )

    @strawberry.field
    async def characters(self, info: "NuInfo") -> list[Character]:
        session = info.context.session
        result = await session.execute(
            select(models.Character)
            .join(models.Character.character_channels)
            .join(models.Channel)
            .where(models.Channel.id == self.id)
        )
        return [Character.from_orm(r) for r in result.scalars().all()]


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
