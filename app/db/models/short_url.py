from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import TIMESTAMP, Column
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.db.models.view_log import URLViewLog


class ShortURL(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_url: str = Field(nullable=False, index=True)
    short_code: str = Field(nullable=False, unique=True, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
    view_logs: Optional[List["URLViewLog"]] = Relationship(back_populates="shorturl")
