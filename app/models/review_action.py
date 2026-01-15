import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ReviewAction(Base):
    __tablename__ = "review_actions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id: Mapped[str] = mapped_column(String, index=True)
    action: Mapped[str] = mapped_column(String)  # approved | rejected
    actor: Mapped[str | None] = mapped_column(String, nullable=True, default="system")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    raw_event_id: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index("idx_review_actions_candidate", "candidate_id"),
        Index("idx_review_actions_timestamp", "timestamp"),
    )
