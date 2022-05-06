import graphene
from sqlalchemy import select
from sqlalchemy.orm import selectinload

import newmu.graphql.types as types
import newmu.models as models


class Query(graphene.ObjectType):
    me = graphene.Field(types.CurrentPlayer, required=True)
    channel = graphene.Field(types.Channel, required=True, id=graphene.Argument(graphene.ID, required=True))
    channels = graphene.List(graphene.NonNull(types.Channel), required=True)
    areas = graphene.List(graphene.NonNull(types.Area), required=True)

    @staticmethod
    async def resolve_me(root, info):
        session = info.context["session"]
        result = await session.execute(
            select(models.Player).options(selectinload(models.Player.characters)).options(selectinload(models.Player.windows)).where(models.Player.id == info.context["player"].id)
        )
        return result.scalar_one()

    @staticmethod
    async def resolve_channel(root, info, id):
        session = info.context["session"]
        result = await session.execute(
            select(models.Channel).where(models.Channel.id == id)
        )
        return result.scalar_one()

    @staticmethod
    async def resolve_channels(root, info):
        session = info.context["session"]
        result = await session.execute(
            select(models.Channel)
        )
        return result.scalars().all()

    @staticmethod
    async def resolve_areas(root, info):
        session = info.context["session"]
        result = await session.execute(
            select(models.Area)
        )
        return result.scalars().all()