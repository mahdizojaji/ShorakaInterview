from datetime import datetime

from pydantic import BaseModel, HttpUrl, field_validator


class ShortURLCreateRequest(BaseModel):
    original_url: HttpUrl


class ShortURLResponse(BaseModel):
    id: int
    original_url: str  # Changed from HttpUrl to str to match model
    short_code: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("original_url", mode="before")
    @classmethod
    def validate_original_url(cls, v):
        """Convert HttpUrl to string if needed"""
        if hasattr(v, "str"):
            return str(v)
        elif isinstance(v, HttpUrl):
            return str(v)
        return v


class ShortURLStatsResponse(BaseModel):
    short_code: str
    original_url: str
    view_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
