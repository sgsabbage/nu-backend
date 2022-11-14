# Import all the models, so that Base has them before being
# imported by Alembic
import nu.core.models  # noqa: F401
from nu.db.base_class import Base  # noqa: F401

__all__ = ["Base"]
