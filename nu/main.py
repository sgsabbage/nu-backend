from dataclasses import dataclass

import strawberry
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext, GraphQLRouter
from strawberry.types import Info

from nu import api
from nu.broadcast import broadcast
from nu.deps import get_player, get_session
from nu.graphql.loaders import Loaders, get_loaders
from nu.graphql.mutations import Mutation
from nu.graphql.queries import Query

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
class Context(BaseContext):
    player: Player
    session: AsyncSession
    loaders: Loaders


NuInfo = Info["Context", "Query"]


async def get_context(
    player: Player = Depends(get_player),
    session: AsyncSession = Depends(get_session),
) -> Context:
    return Context(player=player, session=session, loaders=get_loaders(session))


schema = strawberry.Schema(Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema=schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")


# @app.post("/")
# async def root_post(
#     request: Request,
#     player: Player = Depends(get_player),
#     session: AsyncSession = Depends(get_session),
# ) -> None:
#     loaders = get_loaders(session)
#     async with session.begin():
#         return await GraphQLApp(
#             schema,
#             context_value={"loaders": loaders, "session": session, "player": player},
#         )._handle_http_request(request)


# @app.websocket("/")
# async def root_ws(
#     ws: WebSocket,
#     player: Player = Depends(get_player),
#     session: AsyncSession = Depends(get_session),
# ) -> None:
#     loaders = get_loaders(session)

#     if player is None:
#         await ws.accept()
#         await ws.close(4001)
#         return

#     await GraphQLApp(
#         schema, context_value={"loaders": loaders, "session": session, "player": player}
#     )._run_websocket_server(ws)


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
