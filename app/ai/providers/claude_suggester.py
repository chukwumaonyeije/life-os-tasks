"""
Anthropic Claude Provider Implementation.

Uses Anthropic's Messages API for task extraction.
"""

import json
import logging
import os

from app.ai.contract import AISuggestion, validate_suggestion
from app.ai.prompts import CURRENT_PROMPT_VERSION, get_prompt

logger = logging.getLogger(__name__)


class ClaudeSuggester:
    """Anthropic Claude-based task suggester.

    Environment Variables Required:
        - ANTHROPIC_API_KEY: Anthropic API key
        - AI_MODEL: Model name (default: claude-3-5-sonnet-20241022)
    """

    def __init__(self):
        self.provider_name = "anthropic"
        self.model_name = os.getenv("AI_MODEL", "claude-3-5-sonnet-20241022")
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        # Lazy import to allow optional dependency
        try:
            import anthropic

            self.client = anthropic.Anthropic(
                api_key=self.api_key,
                timeout=10.0,  # 10 second timeout
                max_retries=2,  # 2 retries max
            )
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

    def suggest(self, text: str) -> AISuggestion | None:
        """Extract task suggestion using Anthropic API.

        Args:
            text: Input text (already PII-redacted)

        Returns:
            AISuggestion if successful, None on failure
        """
        try:
            prompt = get_prompt(CURRENT_PROMPT_VERSION).format(text=text)

            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=500,
                temperature=0.3,  # Low temperature for consistency
                system="You are a task extraction assistant. Return only valid JSON with no additional text.",
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract text content from Claude's response
            if not message.content or len(message.content) == 0:
                logger.warning("Claude returned empty content")
                return None

            content = (
                message.content[0].text
                if hasattr(message.content[0], "text")
                else str(message.content[0])
            )

            # Parse JSON response
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.warning(f"Claude response not valid JSON: {e}")
                return None

            # Validate against contract
            suggestion = validate_suggestion(data)
            if not suggestion:
                logger.warning(f"Claude response failed validation: {data}")
                return None

            logger.info(
                f"Claude suggestion: {suggestion.title} (confidence: {suggestion.confidence})"
            )
            return suggestion

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return None
