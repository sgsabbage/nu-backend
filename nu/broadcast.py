from broadcaster import Broadcast

from nu.core.config import settings

broadcast = Broadcast(settings.SQLALCHEMY_DATABASE_URI)
