from asyncio import CancelledError
from typing import TYPE_CHECKING, Any, AsyncGenerator, Callable, Coroutine, TypeVar

import strawberry
from broadcaster import Event
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nu import models
from nu.broadcast import broadcast
from nu.db.session import SessionLocal
from nu.graphql.loaders import get_loaders
from nu.graphql.types import ChannelMessage, Room

if TYPE_CHECKING:
    from nu.main import NuInfo

T = TypeVar("T")


async def subscribe(
    channel: str,
    info: "NuInfo",
    fn: Callable[[Event, AsyncSession], Coroutine[Any, Any, T]],
) -> AsyncGenerator[T | None, None]:
    async with broadcast.subscribe(channel=channel) as subscriber:
        try:
            async for event in subscriber:
                async with SessionLocal.begin() as session:
                    info.context.loaders = get_loaders(session, info.context.player)
                    yield await fn(event, session)
        except CancelledError:
            pass
    yield None


async def sub_channel(event: Event, session: AsyncSession) -> ChannelMessage:
    message_id = event.message
    result = await session.execute(
        select(models.ChannelMessage).where(models.ChannelMessage.id == message_id)
    )
    return ChannelMessage.from_orm(result.scalar_one())


async def sub_room_status(event: Event, session: AsyncSession) -> Room:
    room_id = event.message
    result = await session.execute(select(models.Room).where(models.Room.id == room_id))
    return Room.from_orm(result.scalar_one())


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def channel_messages(
        self, info: "NuInfo"
    ) -> AsyncGenerator[ChannelMessage | None, None]:
        return subscribe("channels", info, sub_channel)

    @strawberry.subscription
    async def room_status(self, info: "NuInfo") -> AsyncGenerator[Room | None, None]:
        return subscribe(f"room-{info.context.player.id}", info, sub_room_status)
