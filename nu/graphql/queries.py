from typing import TYPE_CHECKING

import strawberry
from sqlalchemy import select

import nu.graphql.types as types
import nu.models as models

if TYPE_CHECKING:
    from nu.main import NuInfo


async def get_current_player(info: "NuInfo") -> types.Player:
    session = info.context.session
    result = await session.execute(
        select(models.Player).where(models.Player.id == info.context.player.id)
    )
    return types.Player.from_orm(result.scalar_one())


@strawberry.type
class Query:

    me: types.Player = strawberry.field(resolver=get_current_player)
    # @strawberry.field
    # async def me(self, info: "NuInfo") -> types.CurrentPlayer:
    #

    # channel = graphene.Field(
    #     types.Channel, required=True, id=graphene.Argument(graphene.ID, required=True)
    # )
    # channels = graphene.List(graphene.NonNull(types.Channel), required=True)
    # areas = graphene.List(graphene.NonNull(types.Area), required=True)

    # @staticmethod
    # async def resolve_me(root, info):
    #     session = info.context["session"]
    #     result = await session.execute(
    #         select(models.Player)
    #         .options(selectinload(models.Player.characters))
    #         .options(selectinload(models.Player.windows))
    #         .where(models.Player.id == info.context["player"].id)
    #     )
    #     return result.scalar_one()

    # @staticmethod
    # async def resolve_channel(root, info, id):
    #     session = info.context["session"]
    #     result = await session.execute(
    #         select(models.Channel).where(models.Channel.id == id)
    #     )
    #     return result.scalar_one()

    # @staticmethod
    # async def resolve_channels(root, info):
    #     session = info.context["session"]
    #     result = await session.execute(select(models.Channel))
    #     return result.scalars().all()

    # @staticmethod
    # async def resolve_areas(root, info):
    #     session = info.context["session"]
    #     result = await session.execute(select(models.Area))
    #     return result.scalars().all()
