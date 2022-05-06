# Import all the models, so that Base has them before being
# imported by Alembic
import newmu.models  # noqa: F401
from newmu.db.base_class import Base  # noqa: F401
