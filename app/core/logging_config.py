"""
Logging Configuration: Structured logging for LifeOS-Tasks.

Provides consistent logging across API server and background worker.
All AI-related operations are logged for audit and debugging.
"""

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Usage:
        # In main.py or worker.py startup
        from app.core.logging_config import setup_logging
        setup_logging("INFO")
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Root logger configuration
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set specific logger levels
    logging.getLogger("app.ai").setLevel(logging.INFO)
    logging.getLogger("app.worker").setLevel(logging.INFO)
    logging.getLogger("app.ai.factory").setLevel(logging.INFO)
    logging.getLogger("app.ai.providers").setLevel(logging.INFO)

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at level: {level}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance

    Usage:
        logger = get_logger(__name__)
        logger.info("Message")
    """
    return logging.getLogger(name)


# Logger categories for different subsystems
AI_LOGGER = "app.ai"
WORKER_LOGGER = "app.worker"
API_LOGGER = "app.api"
DB_LOGGER = "app.db"


def log_ai_suggestion(
    logger: logging.Logger,
    event_id: str,
    provider: str,
    model: str,
    success: bool,
    error: str | None = None,
) -> None:
    """Log AI suggestion attempt with structured data.

    Args:
        logger: Logger instance
        event_id: Raw event ID
        provider: AI provider name
        model: Model name
        success: Whether suggestion succeeded
        error: Error message if failed
    """
    if success:
        logger.info(
            f"AI suggestion successful | event={event_id} | provider={provider} | model={model}"
        )
    else:
        logger.warning(
            f"AI suggestion failed | event={event_id} | "
            f"provider={provider} | model={model} | error={error}"
        )


def log_validation_failure(logger: logging.Logger, reason: str, data: dict | None = None) -> None:
    """Log AI output validation failure.

    Args:
        logger: Logger instance
        reason: Why validation failed
        data: Optional data that failed validation
    """
    if data:
        logger.warning(f"AI validation failed: {reason} | data={data}")
    else:
        logger.warning(f"AI validation failed: {reason}")


def log_provider_init(
    logger: logging.Logger, provider: str, model: str, success: bool, error: str | None = None
) -> None:
    """Log AI provider initialization.

    Args:
        logger: Logger instance
        provider: Provider name
        model: Model name
        success: Whether init succeeded
        error: Error message if failed
    """
    if success:
        logger.info(f"AI provider initialized | provider={provider} | model={model}")
    else:
        logger.error(f"AI provider init failed | provider={provider} | error={error}")
