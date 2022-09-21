from strawberry.types import Info

from nu.context import Context
from nu.graphql.queries import Query

NuInfo = Info[Context, Query]
