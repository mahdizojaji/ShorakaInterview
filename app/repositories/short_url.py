from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models.short_url import ShortURL


class ShortURLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_original_url(self, original_url: str) -> Optional[ShortURL]:
        query = select(ShortURL).where(ShortURL.original_url == original_url)
        result = await self.session.exec(query)  # type: ignore
        return result.first()

    async def get_by_code(self, short_code: str) -> Optional[ShortURL]:
        query = select(ShortURL).where(ShortURL.short_code == short_code)
        result = await self.session.exec(query)  # type: ignore
        return result.first()

    async def create(self, original_url: str, short_code: str) -> ShortURL:
        short_url = ShortURL(original_url=original_url, short_code=short_code)

        self.session.add(short_url)
        await self.session.commit()
        await self.session.refresh(short_url)

        return short_url
