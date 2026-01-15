"""
Provider Protocol: Interface for AI suggesters.

This protocol ensures all AI providers implement the same interface,
enabling zero-downtime provider swapping.
"""

from typing import Protocol

from app.ai.contract import AISuggestion


class AISuggester(Protocol):
    """Protocol for AI task suggestion providers.

    All providers must implement this interface.
    Provider-specific logic is encapsulated within implementations.

    Attributes:
        provider_name: Human-readable provider identifier (e.g., 'openai')
        model_name: Specific model being used (e.g., 'gpt-4o-mini')
    """

    provider_name: str
    model_name: str

    def suggest(self, text: str) -> AISuggestion | None:
        """Extract a task suggestion from text.

        Args:
            text: Raw input text (already PII-redacted)

        Returns:
            AISuggestion if successful, None if:
                - AI call fails (timeout, network, API error)
                - Response is malformed
                - Validation fails

        Implementation Requirements:
            - Must enforce timeout (10 seconds max)
            - Must limit retries (2 max)
            - Must validate output via validate_suggestion()
            - Must return None on any failure (no exceptions raised)
            - Must log all failures
        """
        ...
