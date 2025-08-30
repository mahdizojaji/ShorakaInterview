from datetime import datetime

from pydantic import BaseModel


class ViewLogResponse(BaseModel):
    id: int
    shorturl_id: int
    viewed_at: datetime
    processed: bool

    model_config = {"from_attributes": True}


class ShortURLStatsResponse(BaseModel):
    short_code: str
    original_url: str
    view_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
