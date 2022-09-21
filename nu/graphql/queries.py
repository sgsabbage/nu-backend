from typing import TYPE_CHECKING

import strawberry

# async def get_current_player(info: "NuInfo") -> PlayerType:
#     session = info.context.session
#     result = await session.execute(
#         select(Player).where(Player.id == info.context.player.id)
#     )
#     return PlayerType.from_orm(result.scalar_one())


@strawberry.type
class Query:
    pass
    # me: PlayerType = strawberry.field(resolver=get_current_player)

    # @strawberry.field
    # async def areas(self, info: "NuInfo") -> list[types.Area]:
    #     session = info.context.session
    #     result = await session.execute(select(models.Area))
    #     return [types.Area.from_orm(a) for a in result.scalars().all()]

    # @strawberry.field
    # async def rooms(self, info: "NuInfo") -> list[types.Room]:
    #     return await info.context.loaders.rooms.all()

    # @strawberry.field
    # async def channel(self, info: "NuInfo", id: strawberry.ID) -> types.Channel:
    #     c = await info.context.loaders.channels.by_id(UUID(id))
    #     return types.Channel.from_orm(c) if c else None

    # @strawberry.field
    # async def windows(self, info: "NuInfo") -> list[types.Window]:
    #     result = await info.context.session.execute(
    #         select(models.PlayerWindow)
    #         .where(models.PlayerWindow.player_id == info.context.player.id)
    #         .order_by(models.PlayerWindow.position)
    #     )
    #     return [types.Window.from_orm(w) for w in result.scalars().all()]
