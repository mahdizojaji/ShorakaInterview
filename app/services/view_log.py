from app.repositories.view_log import ViewLogRepository


class ViewLogService:
    def __init__(self, repo: ViewLogRepository | None = None, session=None):
        if repo:
            self.repo = repo
        else:
            if session is None:
                raise ValueError("Session must be provided if repo is not given")
            self.repo = ViewLogRepository(session)

    async def log_view(self, shorturl_id: int):
        return await self.repo.create_view_log(shorturl_id)

    async def get_view_count(self, shorturl_id: int) -> int:
        return await self.repo.get_view_count(shorturl_id)
