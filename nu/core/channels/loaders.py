from nu.loaders import BaseLoader

from .models import Channel
from .types import Channel as ChannelType


class ChannelLoader(BaseLoader[Channel, ChannelType]):
    model = Channel
    type = ChannelType

    async def can_see(self, obj: Channel) -> bool:
        return True
