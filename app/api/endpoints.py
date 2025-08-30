from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import RedirectResponse

from app.db.models import ShortURL
from app.db.session import get_session
from app.exceptions.short_url import ShortURLGenerationError, ShortURLNotFoundError
from app.schemas.short_url import ShortURLCreateRequest, ShortURLResponse
from app.schemas.view_log import ShortURLStatsResponse
from app.services.short_url import ShortURLService

router = APIRouter()


@router.post("/shorten", response_model=ShortURLResponse)
async def create_short_url(
    request: ShortURLCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    service = ShortURLService(session=session)
    try:
        short_url: ShortURL = await service.create_short_url(original_url=str(request.original_url))
        return ShortURLResponse(
            id=short_url.id,
            original_url=short_url.original_url,
            short_code=short_url.short_code,
            created_at=short_url.created_at,
        )
    except ShortURLGenerationError:
        raise HTTPException(status_code=400, detail="Could not generate unique short code")


@router.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    session: AsyncSession = Depends(get_session),
):
    service = ShortURLService(session=session)
    try:
        original_url = await service.log_view_and_get_url(short_code)
        return RedirectResponse(url=original_url, status_code=302)
    except ShortURLNotFoundError:
        raise HTTPException(status_code=404, detail="Short URL not found")


@router.get("/{short_code}/stats", response_model=ShortURLStatsResponse)
async def get_short_url_stats(
    short_code: str,
    session: AsyncSession = Depends(get_session),
):
    service = ShortURLService(session=session)
    try:
        stats = await service.get_short_url_with_stats(short_code)
        return ShortURLStatsResponse(
            short_code=stats["short_code"],
            original_url=stats["original_url"],
            view_count=stats["view_count"],
            created_at=stats["created_at"],
        )
    except ShortURLNotFoundError:
        raise HTTPException(status_code=404, detail="Short URL not found")
