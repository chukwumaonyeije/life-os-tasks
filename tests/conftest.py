"""
Pytest configuration and shared fixtures.
"""

import os
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Set test environment before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("AI_PROVIDER", "none")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")


@pytest.fixture
def mock_db_session() -> Generator[MagicMock, None, None]:
    """Provide a mock database session."""
    session = MagicMock(spec=Session)
    yield session


@pytest.fixture
def mock_redis() -> Generator[MagicMock, None, None]:
    """Provide a mock Redis client."""
    with patch("app.core.queue.redis.Redis") as mock:
        yield mock


@pytest.fixture
def test_client(mock_db_session: MagicMock) -> Generator[TestClient, None, None]:
    """Provide a FastAPI test client with mocked dependencies."""
    from app.core.db import get_db
    from app.main import app

    def override_get_db() -> Generator[MagicMock, None, None]:
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def valid_suggestion_data() -> dict:
    """Provide valid AI suggestion data."""
    return {
        "title": "Schedule team meeting",
        "description": "Set up weekly sync with the development team",
        "priority": "medium",
        "confidence": 0.85,
        "rationale": "The text mentions needing to coordinate with team members",
    }


@pytest.fixture
def invalid_suggestion_data_empty_title() -> dict:
    """Provide AI suggestion data with empty title."""
    return {
        "title": "",
        "description": "Some description",
        "priority": "medium",
        "confidence": 0.5,
        "rationale": "Some rationale",
    }


@pytest.fixture
def invalid_suggestion_data_long_title() -> dict:
    """Provide AI suggestion data with title exceeding 60 chars."""
    return {
        "title": "A" * 61,
        "description": "Some description",
        "priority": "medium",
        "confidence": 0.5,
        "rationale": "Some rationale",
    }


@pytest.fixture
def invalid_suggestion_data_bad_priority() -> dict:
    """Provide AI suggestion data with invalid priority."""
    return {
        "title": "Valid title",
        "description": "Some description",
        "priority": "urgent",  # Invalid
        "confidence": 0.5,
        "rationale": "Some rationale",
    }


@pytest.fixture
def invalid_suggestion_data_bad_confidence() -> dict:
    """Provide AI suggestion data with out-of-range confidence."""
    return {
        "title": "Valid title",
        "description": "Some description",
        "priority": "medium",
        "confidence": 1.5,  # Out of range
        "rationale": "Some rationale",
    }
