"""
AI Suggestion Model: Evidence table for AI-generated suggestions.

This table is append-only and exists for audit/replay purposes.
It is NOT part of the workflow - task_candidates remains authoritative.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AISuggestion(Base):
    """AI suggestion evidence record.

    Purpose:
        - Preserve explainability (why did AI suggest this?)
        - Enable replayability (can reproduce suggestion with same inputs)
        - Support provider comparison (OpenAI vs Claude vs local)
        - Audit trail (what prompts/models were used?)

    Invariants:
        - Immutable after creation (append-only)
        - Always linked to raw_event
        - Never directly creates tasks (goes through task_candidates)
    """

    __tablename__ = "ai_suggestions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    raw_event_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    provider: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,  # For provider comparison queries
    )

    model: Mapped[str] = mapped_column(String, nullable=False)

    prompt_version: Mapped[str] = mapped_column(String, nullable=False)

    input_excerpt: Mapped[str] = mapped_column(Text, nullable=False)

    suggestion_json: Mapped[dict] = mapped_column(JSONB, nullable=False)

    rationale: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,  # For time-series queries
    )
