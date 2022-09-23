import os
from heapq import merge

import strawberry
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from strawberry.extensions.tracing.opentelemetry import OpenTelemetryExtension
from strawberry.fastapi import GraphQLRouter
from strawberry.tools import merge_types

from nu import api
from nu.broadcast import broadcast
from nu.context import PlayerContext
from nu.core.channels.queries import Query as ChannelQuery
from nu.core.grid.mutations import Mutation as GridMutation
from nu.core.grid.queries import Query as GridQuery
from nu.core.grid.subscriptions import Subscription as GridSubscription
from nu.core.player.models import Player
from nu.core.player.queries import Query as PlayerQuery
from nu.deps import get_player
from nu.extensions import TransactionExtension

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


async def get_context(
    player: Player = Depends(get_player),
) -> PlayerContext:
    return PlayerContext(player=player)


Query = merge_types("Query", (ChannelQuery, PlayerQuery, GridQuery))
Mutation = merge_types("Mutation", (GridMutation,))
Subscription = merge_types("Subscription", (GridSubscription,))
schema = strawberry.Schema(
    Query,
    mutation=Mutation,
    subscription=Subscription,
    extensions=[TransactionExtension, OpenTelemetryExtension],
)
graphql_app = GraphQLRouter(schema=schema, context_getter=get_context)


def get_graphiql_response() -> HTMLResponse:
    with open(
        os.path.dirname(os.path.abspath(__file__)) + "/static/playground.html"
    ) as f:
        html = f.read()
    return HTMLResponse(html)


setattr(graphql_app, "get_graphiql_response", get_graphiql_response)

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
