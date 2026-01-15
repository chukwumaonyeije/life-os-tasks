"""
AI Provider Factory.

Selects and instantiates AI suggester based on environment configuration.
Handles missing dependencies and configuration gracefully.
"""

import logging
import os

from app.ai.protocol import AISuggester

logger = logging.getLogger(__name__)


def get_suggester() -> AISuggester | None:
    """Get AI suggester based on environment config.

    Returns None if:
        - AI_PROVIDER is 'none' or not set
        - Provider dependencies not installed
        - API keys not configured
        - Provider initialization fails

    Environment Variables:
        - AI_PROVIDER: 'openai' | 'anthropic' | 'none' (default: 'none')
        - AI_MODEL: Model name (provider-specific defaults)
        - OPENAI_API_KEY: Required if provider=openai
        - ANTHROPIC_API_KEY: Required if provider=anthropic

    Returns:
        AISuggester instance or None

    Examples:
        >>> # AI disabled
        >>> os.environ['AI_PROVIDER'] = 'none'
        >>> get_suggester()  # Returns None

        >>> # OpenAI enabled
        >>> os.environ['AI_PROVIDER'] = 'openai'
        >>> os.environ['OPENAI_API_KEY'] = 'sk-...'
        >>> suggester = get_suggester()  # Returns OpenAISuggester
    """
    provider = os.getenv("AI_PROVIDER", "none").lower()

    if provider == "none":
        logger.info("AI provider disabled (AI_PROVIDER=none)")
        return None

    try:
        suggester: AISuggester

        if provider == "openai":
            from app.ai.providers.openai_suggester import OpenAISuggester

            suggester = OpenAISuggester()
            logger.info(f"Initialized OpenAI suggester (model: {suggester.model_name})")
            return suggester

        elif provider == "anthropic":
            from app.ai.providers.claude_suggester import ClaudeSuggester

            suggester = ClaudeSuggester()
            logger.info(f"Initialized Claude suggester (model: {suggester.model_name})")
            return suggester

        else:
            logger.warning(
                f"Unknown AI provider: {provider}. Valid options: openai, anthropic, none"
            )
            return None

    except ImportError as e:
        logger.warning(f"AI provider '{provider}' dependencies not installed: {e}")
        logger.info(f"To enable {provider}, install with: pip install {provider}")
        return None

    except ValueError as e:
        logger.warning(f"AI provider '{provider}' configuration error: {e}")
        return None

    except Exception as e:
        logger.error(f"Failed to initialize AI provider '{provider}': {e}")
        return None
