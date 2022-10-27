from strawberry.types import Info

from nu.context import Context


class Query:
    ...


NuInfo = Info[Context, Query]
