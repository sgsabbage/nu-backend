from aiodataloader import DataLoader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from newmu.models import Character


class DBDataLoader(DataLoader):
    def __init__(self, session: AsyncSession, **kwargs):
        super().__init__(**kwargs)
        self.session = session


class CharacterLoader(DBDataLoader):
    async def batch_load_fn(self, keys):
        async def test_fn():
            result = await self.session.execute(
                select(Character).filter(Character.id.in_(keys))
            )
            chars = result.scalars().all()
            return [next((c for c in chars if c.id == k), None) for k in keys]

        return await test_fn()


def get_loaders(session: AsyncSession):
    return {"char_loader": CharacterLoader(session=session)}
