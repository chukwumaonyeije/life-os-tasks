"""
Prompt Engineering: Versioned, deterministic prompts.

All prompts are versioned to enable replay and A/B testing.
PII redaction is applied before any AI call.
"""

import logging
import re

logger = logging.getLogger(__name__)

# Current prompt version (update when changing prompts)
CURRENT_PROMPT_VERSION = "v1"


# Prompt V1: Single task extraction
PROMPT_V1 = """You are a task extraction assistant. Extract ONE actionable task from the provided text.

**Rules:**
- Title must be imperative (e.g., "Schedule meeting", not "Need to schedule meeting")
- Title must be under 60 characters
- Priority levels:
  * low: informational, nice-to-have
  * medium: should do, moderate importance
  * high: urgent, time-sensitive
- Confidence: 0.0 (very unsure) to 1.0 (completely certain)
- Rationale: Explain in 1-2 sentences why this is a task

**Return ONLY valid JSON (no additional text):**
{{
  "title": "Imperative task title under 60 chars",
  "description": "Additional context and details",
  "priority": "low|medium|high",
  "confidence": 0.0-1.0,
  "rationale": "Why this is a task"
}}

**Input Text:**
{text}

**Your Response (JSON only):**"""


def get_prompt(version: str = CURRENT_PROMPT_VERSION) -> str:
    """Get prompt template by version.

    Args:
        version: Prompt version identifier (e.g., 'v1', 'v2')

    Returns:
        Prompt template string with {text} placeholder

    Raises:
        ValueError: If version not found (defaults to v1 with warning)
    """
    prompts = {"v1": PROMPT_V1}

    if version not in prompts:
        logger.warning(f"Prompt version '{version}' not found, using v1")
        return prompts["v1"]

    return prompts[version]


def redact_pii(text: str) -> str:
    """Redact personally identifiable information from text.

    Applies basic pattern matching to strip:
        - Social Security Numbers (XXX-XX-XXXX)
        - Credit card numbers (16 digits)
        - Email addresses
        - Phone numbers (US format)

    Args:
        text: Raw input text

    Returns:
        Text with PII patterns replaced with [REDACTED] tokens

    Note:
        This is basic protection. For production systems with PHI/PII,
        use specialized libraries like Microsoft Presidio or AWS Comprehend.

    Examples:
        >>> redact_pii("Call 555-123-4567")
        'Call [PHONE-REDACTED]'

        >>> redact_pii("Email me@example.com")
        'Email [EMAIL-REDACTED]'
    """
    redacted = text

    # SSN pattern (XXX-XX-XXXX)
    redacted = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN-REDACTED]", redacted)

    # Credit card numbers (simple: 16 digits with optional spaces/dashes)
    redacted = re.sub(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[CC-REDACTED]", redacted)

    # Email addresses
    redacted = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL-REDACTED]", redacted
    )

    # US phone numbers (multiple formats)
    # Matches: (555) 123-4567, 555-123-4567, 555.123.4567, 5551234567
    redacted = re.sub(
        r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
        "[PHONE-REDACTED]",
        redacted,
    )

    # Log if any redactions occurred
    if redacted != text:
        num_redactions = len(re.findall(r"\[.*?-REDACTED\]", redacted))
        logger.info(f"Redacted {num_redactions} PII pattern(s) from input")

    return redacted


def truncate_for_excerpt(text: str, max_length: int = 500) -> str:
    """Truncate text for storage in input_excerpt field.

    Args:
        text: Original text
        max_length: Maximum characters to retain

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."
