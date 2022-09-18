import os

import strawberry
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from strawberry.extensions.tracing.opentelemetry import OpenTelemetryExtension
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from nu import api
from nu.broadcast import broadcast
from nu.context import Context, PlayerContext
from nu.deps import get_player
from nu.extensions import TransactionExtension
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


NuInfo = Info[Context, Query]


async def get_context(
    player: Player = Depends(get_player),
) -> PlayerContext:
    return PlayerContext(player=player)


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
