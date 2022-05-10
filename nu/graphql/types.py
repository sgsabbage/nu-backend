from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Generic, TypeVar

import strawberry
from sqlalchemy import select

import nu.models as models

if TYPE_CHECKING:
    from nu.db.base_class import Base
    from nu.main import NuInfo

# class Area(graphene.ObjectType):
#     id = graphene.ID(required=True)
#     name = graphene.String(required=True)
#     rooms = graphene.List(graphene.NonNull(lambda: Room), required=True)

#     @staticmethod
#     async def resolve_rooms(root, info) -> models.Room:
#         session = info.context["session"]
#         result = await session.execute(
#             select(models.Room).filter(models.Room.area_id == root.id)
#         )

#         return result.scalars().all()


# class Room(graphene.ObjectType):
#     id = graphene.ID(required=True)
#     name = graphene.String(required=True)
#     area = graphene.Field(Area, required=True)
#     x = graphene.Int(required=True)
#     y = graphene.Int(required=True)
#     exits = graphene.List(graphene.NonNull(lambda: Exit), required=True)

#     @staticmethod
#     async def resolve_area(root, info) -> models.Area:
#         session = info.context["session"]
#         result = await session.execute(
#             select(models.Area).filter(models.Area.id == root.area_id)
#         )
#         return result.scalar_one()

#     @staticmethod
#     async def resolve_exits(root, info) -> models.Room:
#         session = info.context["session"]
#         result = await session.execute(
#             select(models.Exit).filter(models.Exit.start_room_id == root.id)
#         )

#         return result.scalars().all()


# class Exit(graphene.ObjectType):
#     id = graphene.ID(required=True)
#     name = graphene.String(required=True)
#     start_room = graphene.Field(Room, required=True)
#     end_room = graphene.Field(Room, required=True)
#     secret = graphene.Boolean(required=True)

#     @staticmethod
#     async def resolve_start_room(root, info) -> models.Room:
#         session = info.context["session"]
#         result = await session.execute(
#             select(models.Room).filter(models.Room.id == root.start_room_id)
#         )
#         return result.scalar_one()

#     @staticmethod
#     async def resolve_end_room(root, info) -> models.Room:
#         session = info.context["session"]
#         result = await session.execute(
#             select(models.Room).filter(models.Room.id == root.end_room_id)
#         )
#         return result.scalar_one()


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
            select(models.PlayerWindow).filter(models.PlayerWindow.player_id == self.id)
        )
        return [Window.from_orm(w) for w in result.scalars().all()]


@strawberry.type
class Character(BaseType[models.Character]):
    id: strawberry.ID
    name: str
    base_color: str | None


# class Character(graphene.ObjectType):
#     id = graphene.ID(required=True)
#     name = graphene.String(required=True)


# class ChannelMessage(graphene.ObjectType):
#     id = graphene.ID(required=True)
#     timestamp = graphene.DateTime(required=True)
#     message = graphene.String(required=True)
#     character = graphene.Field(Character)
#     channel = graphene.Field(lambda: Channel, required=True)

#     @staticmethod
#     def resolve_character(root, info) -> models.Character:
#         return info.context["loaders"]["char_loader"].load(root.character_id)

#     @staticmethod
#     async def resolve_channel(root, info) -> models.Channel:
#         session = info.context["session"]
#         result = await session.execute(
#             select(models.Channel).filter(models.Channel.id == root.channel_id)
#         )
#         return result.scalar_one()


# class ChannelMessageConnection(relay.Connection):
#     nodes = graphene.List(graphene.NonNull(ChannelMessage), required=True)

#     class Meta:
#         node = ChannelMessage


# class Channel(graphene.ObjectType):
#     id = graphene.ID(required=True)
#     name = graphene.String(required=True)
#     description = graphene.String()
#     messages = graphene.Field(
#         ChannelMessageConnection,
#         first=graphene.Int(),
#         last=graphene.Int(),
#         after=graphene.String(),
#         before=graphene.String(),
#         required=True,
#     )
#     characters = graphene.List(graphene.NonNull(Character), required=True)

#     @staticmethod
#     async def resolve_messages(
#         root, info, first, after, before, last
#     ) -> [models.ChannelMessage]:
#         if first is not None and last is not None:
#             raise GraphQLError("Cannot specify first and last")
#         session = info.context["session"]

#         statement = select(models.ChannelMessage).filter(
#             models.ChannelMessage.channel_id == root.id
#         )

#         bounds_stmnt = select(
#             func.min(models.ChannelMessage.timestamp),
#             func.max(models.ChannelMessage.timestamp),
#         ).where(models.ChannelMessage.channel_id == root.id)
#         bounds = (await session.execute(bounds_stmnt)).first()

#         if after is not None:
#             statement = statement.where(
#                 models.ChannelMessage.timestamp > parser.isoparse(after)
#             )
#         if before is not None:
#             statement = statement.where(
#                 models.ChannelMessage.timestamp < parser.isoparse(before)
#             )

#         if last is None:
#             statement = statement.order_by(models.ChannelMessage.timestamp)
#         else:
#             statement = statement.order_by(desc(models.ChannelMessage.timestamp)).limit(
#                 last
#             )

#         if first is not None:
#             statement = statement.limit(first)

#         result = await session.execute(statement)
#         results: list[models.ChannelMessage] = result.scalars().all()

#         if last:
#             results.reverse()

#         has_next_page = False
#         has_previous_page = False

#         if bounds[0] is None:
#             pass
#         elif results:
#             has_next_page = bounds[1] > results[-1].timestamp
#             has_previous_page = bounds[0] < results[0].timestamp
#         elif before is not None:
#             has_next_page = True
#         elif after is not None:
#             has_previous_page = True

#         pi = PageInfo(has_next_page=has_next_page, has_previous_page=has_previous_page)
#         if results:
#             pi.start_cursor = results[0].timestamp.isoformat()
#             pi.end_cursor = results[-1].timestamp.isoformat()

#         return ChannelMessageConnection(
#             page_info=pi,
#             edges=[{"cursor": r.timestamp.isoformat(), "node": r} for r in results],
#             nodes=results,
#         )

#     @staticmethod
#     async def resolve_characters(root, info):
#         session = info.context["session"]
#         result = await session.execute(
#             select(models.Character)
#             .join(models.Character.character_channels)
#             .join(models.Channel)
#             .where(models.Channel.id == root.id)
#         )
#         return result.scalars().all()


@strawberry.type
class WindowSetting(BaseType[models.PlayerWindow]):
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
    z: int

    @strawberry.field
    async def character(self, info: "NuInfo") -> Character | None:
        return Character.from_orm(
            await info.context.loaders.characters.load(self._model.character_id)
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
