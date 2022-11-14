class BasePlugin:
    NAME: str
    queries: list[type] = []
    mutations: list[type] = []
    subscriptions: list[type] = []

    @classmethod
    def install(cls) -> None:
        pass
