import datetime
from typing import Optional

import strawberry
from dateutil import parser
from graphql import GraphQLError
from sqlalchemy import desc, func, select

from nu.core.player.models import Character
from nu.core.player.types import Character as CharacterType
from nu.graphql.pagination import Connection, Edge, PageInfo
from nu.info import NuInfo
from nu.types import BaseType

from . import models


@strawberry.type
class ChannelMessage(BaseType[models.ChannelMessage]):
    id: strawberry.ID
    timestamp: datetime.datetime
    message: str

    @strawberry.field
    async def character(self, info: "NuInfo") -> Optional[CharacterType]:
        return await info.context.loaders.characters.by_id(self._model.character_id)

    @strawberry.field
    async def channel(self, info: "NuInfo") -> Optional["Channel"]:
        return await info.context.loaders.channels.by_id(self._model.channel_id)


@strawberry.type
class Channel(BaseType[models.Channel]):
    id: strawberry.ID
    name: str
    description: str | None

    @strawberry.field
    async def messages(
        self,
        info: "NuInfo",
        first: int | None = None,
        last: int | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> Connection[ChannelMessage]:
        if first is not None and last is not None:
            raise GraphQLError("Cannot specify first and last")
        session = info.context.session

        stmt = select(models.ChannelMessage).filter(
            models.ChannelMessage.channel_id == self.id
        )

        bounds_stmnt = select(
            func.min(models.ChannelMessage.timestamp),
            func.max(models.ChannelMessage.timestamp),
        ).where(models.ChannelMessage.channel_id == self.id)
        bounds = (await session.execute(bounds_stmnt)).first()

        if after is not None:
            stmt = stmt.where(models.ChannelMessage.timestamp > parser.isoparse(after))
        if before is not None:
            stmt = stmt.where(models.ChannelMessage.timestamp < parser.isoparse(before))

        if last is None:
            stmt = stmt.order_by(models.ChannelMessage.timestamp)
        else:
            stmt = stmt.order_by(desc(models.ChannelMessage.timestamp)).limit(last)

        if first is not None:
            stmt = stmt.limit(first)

        result = await session.execute(stmt)
        results: list[models.ChannelMessage] = result.scalars().all()

        if last:
            results.reverse()

        has_next_page = False
        has_previous_page = False

        if bounds is None or bounds[0] is None:
            pass
        elif results:
            has_next_page = bounds[1] > results[-1].timestamp
            has_previous_page = bounds[0] < results[0].timestamp
        elif before is not None:
            has_next_page = True
        elif after is not None:
            has_previous_page = True

        pi = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=has_previous_page,
            start_cursor=None,
            end_cursor=None,
        )
        if results:
            pi.start_cursor = results[0].timestamp.isoformat()
            pi.end_cursor = results[-1].timestamp.isoformat()

        return Connection[ChannelMessage](
            page_info=pi,
            edges=[
                Edge[ChannelMessage](
                    cursor=r.timestamp.isoformat(), node=ChannelMessage.from_orm(r)
                )
                for r in results
            ],
        )

    @strawberry.field
    async def characters(self, info: "NuInfo") -> list[CharacterType]:
        session = info.context.session
        result = await session.execute(
            select(Character)
            .join(Character.character_channels)
            .join(models.Channel)
            .where(models.Channel.id == self.id)
        )
        return [CharacterType.from_orm(r) for r in result.scalars().all()]
