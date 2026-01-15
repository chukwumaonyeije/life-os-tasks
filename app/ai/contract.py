"""
AI Contract: Strict JSON schema for task suggestions.

This module defines the hard boundary between AI providers and the domain.
Any deviation from this contract results in suggestion discard.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AISuggestion:
    """Validated AI task suggestion.

    This is the ONLY format AI providers may return.
    All fields are validated before construction.
    """

    title: str  # < 60 chars, imperative
    description: str  # Expanded context
    priority: str  # low | medium | high
    confidence: float  # 0.0 - 1.0
    rationale: str  # Why this was suggested


def validate_suggestion(data: dict) -> AISuggestion | None:
    """Validate AI output against contract.

    Args:
        data: Dictionary from AI provider (parsed JSON)

    Returns:
        AISuggestion if valid, None if malformed

    Validation Rules:
        - Must be a dict
        - Title: non-empty, <= 60 chars
        - Priority: must be 'low', 'medium', or 'high'
        - Confidence: float between 0.0 and 1.0
        - Description and rationale: any string (empty allowed)

    On Failure:
        - Logs warning with reason
        - Returns None (caller discards)
    """
    try:
        if not isinstance(data, dict):
            logger.warning(f"AI output not a dict: {type(data)}")
            return None

        # Validate title
        title = data.get("title", "").strip()
        if not title:
            logger.warning("AI output missing or empty title")
            return None
        if len(title) > 60:
            logger.warning(f"AI title too long: {len(title)} chars (max 60)")
            return None

        # Validate priority
        priority = data.get("priority", "medium")
        if priority not in ["low", "medium", "high"]:
            logger.warning(f"Invalid priority: {priority}")
            return None

        # Validate confidence
        try:
            confidence = float(data.get("confidence", 0.0))
            if not (0.0 <= confidence <= 1.0):
                logger.warning(f"Confidence out of range: {confidence}")
                return None
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid confidence value: {e}")
            return None

        # Description and rationale can be any string
        description = data.get("description", "")
        rationale = data.get("rationale", "")

        return AISuggestion(
            title=title,
            description=description,
            priority=priority,
            confidence=confidence,
            rationale=rationale,
        )

    except Exception as e:
        logger.error(f"Unexpected error validating AI suggestion: {e}")
        return None


def suggestion_to_dict(suggestion: AISuggestion) -> dict:
    """Convert AISuggestion to dictionary for JSON storage.

    Args:
        suggestion: Validated AISuggestion instance

    Returns:
        Dictionary suitable for JSONB storage
    """
    return {
        "title": suggestion.title,
        "description": suggestion.description,
        "priority": suggestion.priority,
        "confidence": suggestion.confidence,
        "rationale": suggestion.rationale,
    }
