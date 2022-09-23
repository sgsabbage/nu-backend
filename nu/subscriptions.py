from asyncio import CancelledError
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Callable,
    Coroutine,
    Type,
    TypeVar,
)

from broadcaster import Event
from sqlalchemy.ext.asyncio import AsyncSession

from nu.broadcast import broadcast
from nu.core.grid.loaders import AreaLoader
from nu.core.player.loaders import CharacterLoader, PlayerLoader
from nu.db.session import SessionLocal
from nu.loaders import BaseLoader, get_loaders

if TYPE_CHECKING:
    from nu.info import NuInfo

T = TypeVar("T")


async def subscribe(
    channel: str,
    info: "NuInfo",
    fn: Callable[[Event, AsyncSession, "NuInfo"], Coroutine[Any, Any, T]],
) -> AsyncGenerator[T | None, None]:
    async with broadcast.subscribe(channel=channel) as subscriber:
        try:
            async for event in subscriber:
                async with SessionLocal.begin() as session:
                    classes: list[Type[BaseLoader[Any, Any]]] = [
                        AreaLoader,
                        CharacterLoader,
                        PlayerLoader,
                    ]
                    info.context.loaders = get_loaders(
                        session,
                        info.context.player,
                        classes,
                    )
                    result = await fn(event, session, info)
                    if result:
                        yield result
        except CancelledError:
            pass
    yield None


# async def sub_channel(event: Event, session: AsyncSession) -> ChannelMessage:
#     message_id = event.message
#     result = await session.execute(
#         select(models.ChannelMessage).where(models.ChannelMessage.id == message_id)
#     )
#     return ChannelMessage.from_orm(result.scalar_one())


# async def sub_room_status(event: Event, session: AsyncSession) -> Room:
#     room_id = event.message
#     result = await session.execute(select(models.Room).where(models.Room.id == room_id))
#     return Room.from_orm(result.scalar_one())


# @strawberry.type
# class Subscription:
#     @strawberry.subscription
#     async def channel_messages(
#         self, info: "NuInfo"
#     ) -> AsyncGenerator[ChannelMessage | None, None]:
#         return subscribe("channels", info, sub_channel)

#     @strawberry.subscription
#     async def room_status(self, info: "NuInfo") -> AsyncGenerator[Room | None, None]:
#         return subscribe(f"room-{info.context.player.id}", info, sub_room_status)
