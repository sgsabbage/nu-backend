from datetime import datetime

import graphene
from graphql import GraphQLError
from sqlalchemy import select
from sqlalchemy.exc import InvalidRequestError, StatementError
from sqlalchemy.orm import selectinload

from newmu import models
from newmu.graphql import types
from newmu.models import PlayerWindowSetting


class WindowSettingInput(graphene.InputObjectType):
    key = graphene.String(required=True)
    value = graphene.String(required=True)


class UpdateWindowInput(graphene.InputObjectType):
    id = graphene.UUID(required=True)

    character_id = graphene.UUID()
    top = graphene.Int()
    left = graphene.Int()
    width = graphene.Int()
    height = graphene.Int()
    settings = graphene.InputField(graphene.List(WindowSettingInput))

    z = graphene.Int()


class UpdateWindow(graphene.Mutation):
    class Arguments:
        input = UpdateWindowInput(required=True)

    window = graphene.Field(types.Window)

    @staticmethod
    async def mutate(root, info, input: UpdateWindowInput):
        session = info.context["session"]
        try:
            result = await session.execute(
                select(models.PlayerWindow)
                .filter(models.PlayerWindow.id == input.id)
                .options(selectinload(models.PlayerWindow.settings))
            )
            window = result.scalar_one()
        except (InvalidRequestError, StatementError) as e:
            raise GraphQLError(f"Window '{input.id}' does not exist")

        if input.character_id:
            try:
                character = await session.execute(
                    select(models.Character).filter(
                        models.Character.id == input.character_id
                    )
                )
                window.character = character.scalar_one()
            except (InvalidRequestError, StatementError) as e:
                raise GraphQLError(f"Character '{input.character_id}' does not exist")
        for arg in ["top", "left", "width", "height", "z"]:
            if (val := getattr(input, arg)) is not None:
                setattr(window, arg, val)
        if input.settings is not None:
            settings = []
            for setting in input.settings:
                new_setting = PlayerWindowSetting(
                    key=setting["key"], value=setting["value"], window=window
                )
                session.add(new_setting)
                settings.append(new_setting)
            window.settings = settings
        await session.flush()

        return UpdateWindow(window=window)


class CloseWindowInput(graphene.InputObjectType):
    id = graphene.UUID(required=True)


class CloseWindow(graphene.Mutation):
    class Arguments:
        input = CloseWindowInput(required=True)

    ok = graphene.Boolean(required=True)

    @staticmethod
    async def mutate(root, info, input: CloseWindowInput):
        session = info.context["session"]
        result = await session.execute(
            select(models.PlayerWindow).filter(models.PlayerWindow.id == input.id)
        )
        window = result.scalar_one()
        await session.delete(window)
        return CloseWindow(ok=True)


class SendChannelMessageInput(graphene.InputObjectType):
    id = graphene.UUID(required=True)
    character_id = graphene.UUID(required=True)
    message = graphene.String(required=True)


class SendChannelMessage(graphene.Mutation):
    class Arguments:
        input = SendChannelMessageInput(required=True)

    message = graphene.Field(graphene.NonNull(types.ChannelMessage))

    @staticmethod
    async def mutate(root, info, input: SendChannelMessageInput):
        session = info.context["session"]
        cm = models.ChannelMessage(
            channel_id=input.id,
            character_id=input.character_id,
            message=input.message,
            timestamp=datetime.now(),
        )
        session.add(cm)
        await session.flush()
        await session.execute(f"NOTIFY channels, '{cm.id}'")
        return SendChannelMessage(message=cm)


class OpenWindowInput(graphene.InputObjectType):
    component = graphene.String(required=True)
    character_id = graphene.UUID(required=True)
    top = graphene.Int(required=True)
    left = graphene.Int(required=True)
    width = graphene.Int(required=True)
    height = graphene.Int(required=True)
    z = graphene.Int(required=True)


class OpenWindow(graphene.Mutation):
    class Arguments:
        input = OpenWindowInput(required=True)

    window = graphene.Field(types.Window, required=True)

    @staticmethod
    async def mutate(root, info, input: OpenWindowInput):
        session = info.context["session"]
        w = models.PlayerWindow(
            name=input.component,
            component=input.component,
            z=input.z,
            width=input.width,
            height=input.height,
            top=input.top,
            left=input.left,
            player_id=info.context["player"].id,
            character_id=input.character_id,
        )
        session.add(w)
        await session.flush()
        return OpenWindow(window=w)


class Mutation(graphene.ObjectType):
    close_window = CloseWindow.Field()
    open_window = OpenWindow.Field(required=True)
    update_window = UpdateWindow.Field()
    send_channel_message = SendChannelMessage.Field()
