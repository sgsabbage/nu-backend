from typing import TYPE_CHECKING, AsyncIterator

import strawberry
from sqlalchemy import select

from nu import models
from nu.broadcast import broadcast
from nu.graphql.types import ChannelMessage

if TYPE_CHECKING:
    from nu.main import NuInfo


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def channel_messages(self, info: "NuInfo") -> AsyncIterator[ChannelMessage]:
        session = info.context.session
        async with broadcast.subscribe(channel="channels") as subscriber:
            async for event in subscriber:
                async with session.begin() as trans:
                    message_id = event.message
                    result = await trans.execute(
                        select(models.ChannelMessage).filter(
                            models.ChannelMessage.id == message_id
                        )
                    )
                    yield ChannelMessage.from_orm(result.scalar_one())
