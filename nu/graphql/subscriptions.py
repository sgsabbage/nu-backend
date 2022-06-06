from asyncio import CancelledError
from typing import TYPE_CHECKING, AsyncGenerator, AsyncIterator

import strawberry
from sqlalchemy import select

from nu import models
from nu.broadcast import broadcast
from nu.db.session import SessionLocal
from nu.graphql.loaders import get_loaders
from nu.graphql.types import ChannelMessage

if TYPE_CHECKING:
    from nu.main import NuInfo


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def channel_messages(
        self, info: "NuInfo"
    ) -> AsyncGenerator[ChannelMessage | None, None]:
        async with broadcast.subscribe(channel="channels") as subscriber:
            try:
                async for event in subscriber:
                    async with SessionLocal.begin() as session:
                        # TODO: This should be more elegant becuase I don't want to do this
                        # for every subscriber
                        info.context.loaders = get_loaders(session)
                        message_id = event.message
                        result = await session.execute(
                            select(models.ChannelMessage).where(
                                models.ChannelMessage.id == message_id
                            )
                        )
                        yield ChannelMessage.from_orm(result.scalar_one())
            except CancelledError:
                pass
        yield None
