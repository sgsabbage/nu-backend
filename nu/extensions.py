from typing import Any, Type

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.extensions import Extension
from strawberry.utils.await_maybe import AwaitableOrValue

from nu.context import Context, PlayerContext
from nu.core.loaders import CharacterLoader, PlayerLoader
from nu.db.session import SessionLocal
from nu.loaders import BaseLoader, get_loaders


class TransactionExtension(Extension):
    async def on_request_start(self) -> AwaitableOrValue[None]:  # type: ignore
        c: PlayerContext = self.execution_context.context
        session = SessionLocal()
        await session.begin()

        classes: list[Type[BaseLoader[Any, Any]]] = [
            CharacterLoader,
            PlayerLoader,
        ]

        context = Context(
            player=c.player,
            loaders=get_loaders(session, c.player, classes),
            session=session,
        )
        context.request = c.request
        context.background_tasks = c.background_tasks
        context.response = c.response
        self.execution_context.context = context

    async def on_request_end(self) -> AwaitableOrValue[None]:  # type: ignore
        s: AsyncSession = self.execution_context.context.session
        try:
            if self.execution_context.errors:
                await s.rollback()
            else:
                await s.commit()
        finally:
            await s.close()
