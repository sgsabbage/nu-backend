import graphene
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket
from starlette_graphene3 import GraphQLApp, make_playground_handler

from nu import api
from nu.broadcast import broadcast
from nu.deps import get_player, get_session
from nu.graphql.loaders import get_loaders
from nu.graphql.mutations import Mutation
from nu.graphql.queries import Query
from nu.graphql.subscriptions import Subscription
from nu.models import Player

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
async def startup_event() -> None:
    await broadcast.disconnect()


schema = graphene.Schema(query=Query, subscription=Subscription, mutation=Mutation)


@app.get("/")
def root(request: Request) -> Response:
    return make_playground_handler()(request)


@app.post("/")
async def root_post(
    request: Request,
    player: Player = Depends(get_player),
    session: AsyncSession = Depends(get_session),
) -> None:
    loaders = get_loaders(session)
    async with session.begin():
        return await GraphQLApp(
            schema,
            context_value={"loaders": loaders, "session": session, "player": player},
        )._handle_http_request(request)


@app.websocket("/")
async def root_ws(
    ws: WebSocket,
    player: Player = Depends(get_player),
    session: AsyncSession = Depends(get_session),
) -> None:
    loaders = get_loaders(session)

    if player is None:
        await ws.accept()
        await ws.close(4001)
        return

    await GraphQLApp(
        schema, context_value={"loaders": loaders, "session": session, "player": player}
    )._run_websocket_server(ws)


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
