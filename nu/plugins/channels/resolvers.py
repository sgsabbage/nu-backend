from sqlalchemy import select

from nu.core.types import Character as CharacterType
from nu.info import NuInfo

from .models import Channel as ChannelModel
from .models import ChannelCharacter
from .types import Channel as ChannelType


async def get_character_channels(
    root: CharacterType, info: NuInfo
) -> list[ChannelType]:
    session = info.context.session
    result = await session.execute(
        select(ChannelModel)
        .join(ChannelModel.channel_characters)
        .where(ChannelCharacter.character_id == root.id)
    )
    return [ChannelType.from_orm(r) for r in result.scalars().all()]
