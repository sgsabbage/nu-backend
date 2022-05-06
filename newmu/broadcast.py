from broadcaster import Broadcast

from newmu.core.config import settings

broadcast = Broadcast(settings.SQLALCHEMY_DATABASE_URI)
