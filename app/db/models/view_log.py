from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import TIMESTAMP, Column, Field, Index, Relationship, SQLModel

if TYPE_CHECKING:
    from app.db.models.short_url import ShortURL


class URLViewLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shorturl_id: int = Field(foreign_key="shorturl.id", nullable=False, index=True)
    shorturl: Optional["ShortURL"] = Relationship(back_populates="view_logs")
    viewed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
    )
    processed: bool = Field(default=False, nullable=False, index=True)

    __table_args__ = (Index("is_shorturl_processed", "shorturl_id", "processed"),)
