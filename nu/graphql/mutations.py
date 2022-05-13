from typing import TYPE_CHECKING, Optional

import strawberry
from graphql import GraphQLError
from sqlalchemy import select
from sqlalchemy.exc import InvalidRequestError, StatementError
from sqlalchemy.orm import selectinload

from nu import models
from nu.graphql import types
from nu.models import PlayerWindowSetting

if TYPE_CHECKING:
    from nu.main import NuInfo


@strawberry.input
class WindowSettingInput:
    key: str
    value: str


@strawberry.input
class UpdateWindowInput:
    id: strawberry.ID

    character_id: strawberry.ID | None = None
    top: int | None = None
    left: int | None = None
    width: int | None = None
    height: int | None = None
    settings: list[WindowSettingInput] | None = None
    z: int | None = None


@strawberry.type
class UpdateWindowResult:
    window: types.Window


@strawberry.input
class CloseWindowInput:
    id: strawberry.ID


@strawberry.type
class CloseWindowResult:
    ok: bool


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def update_window(
        self, info: "NuInfo", input: UpdateWindowInput
    ) -> UpdateWindowResult:
        session = info.context.session
        try:
            result = await session.execute(
                select(models.PlayerWindow)
                .filter(models.PlayerWindow.id == input.id)
                .options(selectinload(models.PlayerWindow.settings))
            )
            window = result.scalar_one()
        except (InvalidRequestError, StatementError):
            raise GraphQLError(f"Window '{input.id}' does not exist")

        if input.character_id:
            try:
                character = await session.execute(
                    select(models.Character).filter(
                        models.Character.id == input.character_id
                    )
                )
                window.character = character.scalar_one()
            except (InvalidRequestError, StatementError):
                raise GraphQLError(f"Character '{input.character_id}' does not exist")

        for arg in ["top", "left", "width", "height", "z"]:
            if (val := getattr(input, arg)) is not None:
                setattr(window, arg, val)
        if input.settings is not None:
            settings = []
            for setting in input.settings:
                new_setting = PlayerWindowSetting(
                    key=setting.key, value=setting.value, window=window
                )
                session.add(new_setting)
                settings.append(new_setting)
            window.settings = settings
        await session.flush()

        return UpdateWindowResult(window=types.Window.from_orm(window))

    @strawberry.mutation
    async def close_window(
        self, info: "NuInfo", input: CloseWindowInput
    ) -> CloseWindowResult:
        session = info.context.session
        result = await session.execute(
            select(models.PlayerWindow).filter(models.PlayerWindow.id == input.id)
        )
        window = result.scalar_one()
        await session.delete(window)
        return CloseWindowResult(ok=True)


# class SendChannelMessageInput(graphene.InputObjectType):
#     id = graphene.UUID(required=True)
#     character_id = graphene.UUID(required=True)
#     message = graphene.String(required=True)


# class SendChannelMessage(graphene.Mutation):
#     class Arguments:
#         input = SendChannelMessageInput(required=True)

#     message = graphene.Field(graphene.NonNull(types.ChannelMessage))

#     @staticmethod
#     async def mutate(root, info, input: SendChannelMessageInput):
#         session = info.context["session"]
#         cm = models.ChannelMessage(
#             channel_id=input.id,
#             character_id=input.character_id,
#             message=input.message,
#             timestamp=datetime.now(),
#         )
#         session.add(cm)
#         await session.flush()
#         await session.execute(f"NOTIFY channels, '{cm.id}'")
#         return SendChannelMessage(message=cm)


# class OpenWindowInput(graphene.InputObjectType):
#     component = graphene.String(required=True)
#     character_id = graphene.UUID(required=True)
#     top = graphene.Int(required=True)
#     left = graphene.Int(required=True)
#     width = graphene.Int(required=True)
#     height = graphene.Int(required=True)
#     z = graphene.Int(required=True)


# class OpenWindow(graphene.Mutation):
#     class Arguments:
#         input = OpenWindowInput(required=True)

#     window = graphene.Field(types.Window, required=True)

#     @staticmethod
#     async def mutate(root, info, input: OpenWindowInput):
#         session = info.context["session"]
#         w = models.PlayerWindow(
#             name=input.component,
#             component=input.component,
#             z=input.z,
#             width=input.width,
#             height=input.height,
#             top=input.top,
#             left=input.left,
#             player_id=info.context["player"].id,
#             character_id=input.character_id,
#         )
#         session.add(w)
#         await session.flush()
#         return OpenWindow(window=w)
