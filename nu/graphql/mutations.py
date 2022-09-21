# from datetime import datetime
# from typing import TYPE_CHECKING
# from uuid import UUID

# import strawberry
# from graphql import GraphQLError
# from sqlalchemy import select, text
# from sqlalchemy.exc import InvalidRequestError, StatementError
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import selectinload

# from nu import models, types
# from nu.models import PlayerWindowSetting

# if TYPE_CHECKING:
#     from nu.main import NuInfo


# async def get_player_with_windows(
#     player_id: UUID, session: AsyncSession
# ) -> models.Player:
#     result = await session.execute(
#         select(models.Player)
#         .options(selectinload(models.Player.windows))
#         .where(models.Player.id == player_id)
#     )
#     p: models.Player = result.scalar_one()
#     return p


# def get_window_index(player: models.Player, window_id: UUID) -> int | None:
#     for index, w in enumerate(player.windows):
#         if w.id == window_id:
#             return index
#     return None


# @strawberry.input
# class WindowSettingInput:
#     key: str
#     value: str


# @strawberry.input
# class UpdateWindowInput:
#     id: UUID

#     character_id: UUID | None = None
#     name: str | None = None
#     top: int | None = None
#     left: int | None = None
#     width: int | None = None
#     height: int | None = None
#     settings: list[WindowSettingInput] | None = None
#     z: int | None = None


# @strawberry.type
# class UpdateWindowResult:
#     window: types.Window


# @strawberry.input
# class CloseWindowInput:
#     id: UUID


# @strawberry.type
# class CloseWindowResult:
#     ok: bool


# @strawberry.type
# class WindowOrderResult:
#     windows: list[types.Window]


# @strawberry.input
# class SendChannelMessageInput:
#     id: UUID
#     character_id: UUID
#     message: str


# @strawberry.type
# class SendChannelMessageResult:
#     message: types.ChannelMessage


# @strawberry.input
# class UpdateRoomInput:
#     id: UUID

#     name: str | None = None
#     description: str | None = None


# @strawberry.input
# class UpdateChannelInput:
#     name: str | None = None
#     description: str | None = None


# @strawberry.type
# class UpdateRoomResult:
#     room: types.Room


# @strawberry.type
# class UpdateChannelResult:
#     channel: types.Channel


# @strawberry.type
# class Mutation:
#     @strawberry.mutation
#     async def update_window(
#         self, info: "NuInfo", input: UpdateWindowInput
#     ) -> UpdateWindowResult:
#         session = info.context.session
#         try:
#             result = await session.execute(
#                 select(models.PlayerWindow)
#                 .filter(models.PlayerWindow.id == input.id)
#                 .options(selectinload(models.PlayerWindow.settings))
#             )
#             window = result.scalar_one()
#         except (InvalidRequestError, StatementError):
#             raise GraphQLError(f"Window '{input.id}' does not exist")

#         if input.character_id:
#             try:
#                 character = await session.execute(
#                     select(models.Character).filter(
#                         models.Character.id == input.character_id
#                     )
#                 )
#                 window.character = character.scalar_one()
#             except (InvalidRequestError, StatementError):
#                 raise GraphQLError(f"Character '{input.character_id}' does not exist")

#         for arg in ["top", "left", "width", "height", "name"]:
#             if (val := getattr(input, arg)) is not None:
#                 setattr(window, arg, val)
#         if input.settings is not None:
#             settings = []
#             for setting in input.settings:
#                 new_setting = PlayerWindowSetting(
#                     key=setting.key, value=setting.value, window=window
#                 )
#                 session.add(new_setting)
#                 settings.append(new_setting)
#             window.settings = settings
#         await session.flush()

#         return UpdateWindowResult(window=types.Window.from_orm(window))

#     @strawberry.mutation
#     async def close_window(
#         self, info: "NuInfo", input: CloseWindowInput
#     ) -> CloseWindowResult:
#         session = info.context.session
#         result = await session.execute(
#             select(models.PlayerWindow).filter(models.PlayerWindow.id == input.id)
#         )
#         window = result.scalar_one()
#         await session.delete(window)
#         return CloseWindowResult(ok=True)

#     @strawberry.mutation
#     async def bring_window_to_front(
#         self, info: "NuInfo", id: UUID
#     ) -> WindowOrderResult:

#         session = info.context.session
#         p = await get_player_with_windows(info.context.player.id, session)
#         index = get_window_index(p, id)

#         if index is None:
#             raise GraphQLError(f"Window '{id}' does not exist")
#         p.windows.insert(0, p.windows.pop(index))
#         p.windows.reorder()
#         await session.flush()
#         return WindowOrderResult(windows=[types.Window.from_orm(w) for w in p.windows])

#     @strawberry.mutation
#     async def send_window_to_back(self, info: "NuInfo", id: UUID) -> WindowOrderResult:

#         session = info.context.session
#         p = await get_player_with_windows(info.context.player.id, session)
#         index = get_window_index(p, id)

#         if index is None:
#             raise GraphQLError(f"Window '{id}' does not exist")
#         p.windows.append(p.windows.pop(index))
#         p.windows.reorder()
#         await session.flush()
#         return WindowOrderResult(windows=[types.Window.from_orm(w) for w in p.windows])

#     @strawberry.mutation
#     async def send_channel_message(
#         self, info: "NuInfo", input: SendChannelMessageInput
#     ) -> SendChannelMessageResult:
#         session = info.context.session
#         channel = (
#             await session.execute(
#                 select(models.Channel).where(models.Channel.id == input.id)
#             )
#         ).scalar_one()

#         char = (
#             await session.execute(
#                 select(models.Character).where(
#                     models.Character.id == input.character_id
#                 )
#             )
#         ).scalar_one()
#         cm = models.ChannelMessage(
#             channel=channel,
#             character=char,
#             message=input.message,
#             timestamp=datetime.now().astimezone(),
#         )

#         session.add(cm)
#         await session.flush()
#         await session.execute(text(f"NOTIFY channels, '{cm.id}'"))
#         return SendChannelMessageResult(message=types.ChannelMessage.from_orm(cm))

#     @strawberry.mutation
#     async def update_room(
#         self, info: "NuInfo", input: UpdateRoomInput
#     ) -> UpdateRoomResult:
#         session = info.context.session
#         room: models.Room = (
#             await session.execute(
#                 select(models.Room)
#                 .options(selectinload(models.Room.characters))
#                 .where(models.Room.id == input.id)
#             )
#         ).scalar_one()

#         if input.description:
#             room.description = input.description
#         if input.name:
#             room.name = input.name

#         players = set()
#         for char in room.characters:
#             players.add(char.player_id)

#         for player_id in players:
#             await session.execute(
#                 text(f"SELECT pg_notify('room-{player_id}', '{room.id}')")
#             )

#         return UpdateRoomResult(room=types.Room.from_orm(room))

#     @strawberry.mutation
#     async def update_channel(
#         self, info: "NuInfo", id: strawberry.ID, input: UpdateChannelInput
#     ) -> UpdateChannelResult:
#         session = info.context.session
#         channel: models.Channel = (
#             await session.execute(select(models.Channel).where(models.Channel.id == id))
#         ).scalar_one()

#         if input.description:
#             channel.description = input.description
#         if input.name:
#             channel.name = input.name

#         return UpdateChannelResult(channel=types.Channel.from_orm(channel))


# # @strawberry.schema_directive
# # class SendChannelMessage(graphene.Mutation):
# #     class Arguments:
# #         input = SendChannelMessageInput(required=True)

# #     message = graphene.Field(graphene.NonNull(types.ChannelMessage))

# #     @staticmethod
# #     async def mutate(root, info, input: SendChannelMessageInput):
# #


# # class OpenWindowInput(graphene.InputObjectType):
# #     component = graphene.String(required=True)
# #     character_id = graphene.UUID(required=True)
# #     top = graphene.Int(required=True)
# #     left = graphene.Int(required=True)
# #     width = graphene.Int(required=True)
# #     height = graphene.Int(required=True)
# #     z = graphene.Int(required=True)


# # class OpenWindow(graphene.Mutation):
# #     class Arguments:
# #         input = OpenWindowInput(required=True)

# #     window = graphene.Field(types.Window, required=True)

# #     @staticmethod
# #     async def mutate(root, info, input: OpenWindowInput):
# #         session = info.context["session"]
# #         w = models.PlayerWindow(
# #             name=input.component,
# #             component=input.component,
# #             z=input.z,
# #             width=input.width,
# #             height=input.height,
# #             top=input.top,
# #             left=input.left,
# #             player_id=info.context["player"].id,
# #             character_id=input.character_id,
# #         )
# #         session.add(w)
# #         await session.flush()
# #         return OpenWindow(window=w)
