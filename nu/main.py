from __future__ import annotations

from dataclasses import dataclass

import strawberry
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.extensions import Extension
from strawberry.fastapi import BaseContext, GraphQLRouter
from strawberry.types import Info
from strawberry.utils.await_maybe import AwaitableOrValue

from nu import api
from nu.broadcast import broadcast
from nu.db.session import SessionLocal
from nu.deps import get_player
from nu.graphql.loaders import Loaders, get_loaders
from nu.graphql.mutations import Mutation
from nu.graphql.queries import Query
from nu.graphql.subscriptions import Subscription

# from nu.graphql.mutations import Mutation
# from nu.graphql.subscriptions import Subscription
from nu.models import Player

# from nu.graphql.loaders import get_loaders


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)


@app.on_event("startup")
async def broadcast_connect() -> None:
    await broadcast.connect()


@app.on_event("shutdown")
async def broadcase_disconnect() -> None:
    await broadcast.disconnect()


@dataclass
class PlayerContext(BaseContext):
    player: Player


@dataclass
class Context(BaseContext):
    player: Player
    session: AsyncSession
    loaders: Loaders


NuInfo = Info["Context", "Query"]


async def get_context(
    player: Player = Depends(get_player),
) -> PlayerContext:
    return PlayerContext(player=player)


class TestExtension(Extension):
    async def on_request_start(self) -> AwaitableOrValue[None]:  # type: ignore
        c: PlayerContext = self.execution_context.context
        session = SessionLocal()
        await session.begin()

        context = Context(
            player=c.player, loaders=get_loaders(session), session=session
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


schema = strawberry.Schema(
    Query, mutation=Mutation, subscription=Subscription, extensions=[TestExtension]
)
graphql_app = GraphQLRouter(schema=schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")


def start() -> None:
    """Launched with `poetry run start` at root level"""
    uvicorn.run(
        "nu.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="warning",
        debug=True,
    )


if __name__ == "__main__":
    start()
