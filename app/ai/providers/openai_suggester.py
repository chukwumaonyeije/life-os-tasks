"""
OpenAI Provider Implementation.

Uses OpenAI's Chat Completions API for task extraction.
"""

import json
import logging
import os

from app.ai.contract import AISuggestion, validate_suggestion
from app.ai.prompts import CURRENT_PROMPT_VERSION, get_prompt

logger = logging.getLogger(__name__)


class OpenAISuggester:
    """OpenAI-based task suggester.

    Environment Variables Required:
        - OPENAI_API_KEY: OpenAI API key
        - AI_MODEL: Model name (default: gpt-4o-mini)
    """

    def __init__(self):
        self.provider_name = "openai"
        self.model_name = os.getenv("AI_MODEL", "gpt-4o-mini")
        self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        # Lazy import to allow optional dependency
        try:
            import openai

            self.client = openai.OpenAI(
                api_key=self.api_key,
                timeout=10.0,  # 10 second timeout
                max_retries=2,  # 2 retries max
            )
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

    def suggest(self, text: str) -> AISuggestion | None:
        """Extract task suggestion using OpenAI API.

        Args:
            text: Input text (already PII-redacted)

        Returns:
            AISuggestion if successful, None on failure
        """
        try:
            prompt = get_prompt(CURRENT_PROMPT_VERSION).format(text=text)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a task extraction assistant. Return only valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Low temperature for consistency
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                logger.warning("OpenAI returned empty content")
                return None

            # Parse JSON response
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.warning(f"OpenAI response not valid JSON: {e}")
                return None

            # Validate against contract
            suggestion = validate_suggestion(data)
            if not suggestion:
                logger.warning(f"OpenAI response failed validation: {data}")
                return None

            logger.info(
                f"OpenAI suggestion: {suggestion.title} (confidence: {suggestion.confidence})"
            )
            return suggestion

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
