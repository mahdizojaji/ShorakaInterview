from app.db.models.short_url import ShortURL
from app.exceptions.short_url import ShortURLGenerationError, ShortURLNotFoundError
from app.repositories.short_url import ShortURLRepository
from app.services.view_log import ViewLogService
from app.utils.shortener import generate_short_code
from app.utils.url import normalize_url


class ShortURLService:
    def __init__(self, repo: ShortURLRepository | None = None, session=None):
        if repo:
            self.repo = repo
        else:
            if session is None:
                raise ValueError("Session must be provided if repo is not given")
            self.repo = ShortURLRepository(session)

    async def _generate_unique_short_code(self, attempts: int = 5) -> str:
        for _ in range(attempts):
            code = generate_short_code()
            if not await self.repo.get_by_code(code):
                return code
        raise ShortURLGenerationError("Could not generate unique short code")

    async def create_short_url(self, original_url: str) -> ShortURL:
        original_url = normalize_url(original_url)
        existing: ShortURL = await self.repo.get_by_original_url(original_url)
        if existing:
            return existing
        short_code = await self._generate_unique_short_code()
        short_url: ShortURL = await self.repo.create(original_url, short_code)
        return short_url

    async def get_original_url(self, short_code: str) -> str:
        short_url = await self.repo.get_by_code(short_code)
        if not short_url:
            raise ShortURLNotFoundError(f"Short URL '{short_code}' not found")
        return short_url.original_url

    async def get_short_url_with_stats(self, short_code: str):
        short_url = await self.repo.get_by_code(short_code)
        if not short_url:
            raise ShortURLNotFoundError(f"Short URL '{short_code}' not found")

        view_service = ViewLogService(session=self.repo.session)
        view_count = await view_service.get_view_count(short_url.id)

        return {
            "short_code": short_url.short_code,
            "original_url": short_url.original_url,
            "view_count": view_count,
            "created_at": short_url.created_at,
        }

    async def log_view_and_get_url(self, short_code: str) -> str:
        short_url = await self.repo.get_by_code(short_code)
        if not short_url:
            raise ShortURLNotFoundError(f"Short URL '{short_code}' not found")

        view_service = ViewLogService(session=self.repo.session)
        await view_service.log_view(short_url.id)

        return short_url.original_url
