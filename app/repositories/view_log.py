from sqlmodel import func, insert, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models.view_log import URLViewLog


class ViewLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_view_log(self, shorturl_id: int) -> URLViewLog:
        view_log = URLViewLog(shorturl_id=shorturl_id)
        query = (
            insert(URLViewLog)
            .values(shorturl_id=view_log.shorturl_id, viewed_at=view_log.viewed_at, processed=view_log.processed)
            .returning(URLViewLog)
        )

        result = await self.session.exec(query)  # type: ignore
        await self.session.commit()
        return result.first()

    async def get_view_count(self, shorturl_id: int) -> int:
        query = select(func.count(URLViewLog.id)).where(URLViewLog.shorturl_id == shorturl_id)
        result = await self.session.exec(query)  # type: ignore
        return result.first() or 0
