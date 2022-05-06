import graphene
from sqlalchemy import select

from newmu.graphql import types
from newmu.broadcast import broadcast
from newmu import models


class Subscription(graphene.ObjectType):
    channel_messages = graphene.Field(types.ChannelMessage)

    @staticmethod
    async def subscribe_channel_messages(root, info):
        session = info.context["session"]
        async with broadcast.subscribe(channel="channels") as subscriber:
            async for event in subscriber:
                async with session.begin():
                    message_id = event.message
                    result = await session.execute(
                        select(models.ChannelMessage).filter(models.ChannelMessage.id == message_id)
                    )
                    yield result.scalar_one()
