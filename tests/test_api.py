"""
Integration tests for API endpoints.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_returns_ok(self, test_client: TestClient) -> None:
        """Health endpoint should return status ok."""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestDictationIngestion:
    """Tests for /ingest/dictation endpoint."""

    def test_ingest_dictation_success(
        self, test_client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Valid dictation should be ingested successfully."""
        with patch("app.ingest_dictation.enqueue_raw_event"):
            response = test_client.post(
                "/ingest/dictation",
                json={"text": "Schedule a meeting with John tomorrow"},
            )

        assert response.status_code == 200
        assert response.json() == {"ok": True}
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_ingest_dictation_missing_text(self, test_client: TestClient) -> None:
        """Missing text field should raise KeyError."""
        with pytest.raises(KeyError):
            test_client.post("/ingest/dictation", json={})


class TestReviewEndpoints:
    """Tests for /api/review endpoints."""

    def test_get_review_queue_empty(
        self, test_client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Empty review queue should return empty list."""
        # Mock query chain
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query

        response = test_client.get("/api/review")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_review_queue_with_candidates(
        self, test_client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Review queue should return pending candidates."""
        from datetime import datetime

        # Create mock candidate
        mock_candidate = MagicMock()
        mock_candidate.id = "test-id-123"
        mock_candidate.title = "Test task"
        mock_candidate.description = "Test description"
        mock_candidate.priority = "medium"
        mock_candidate.created_at = datetime(2024, 1, 15, 10, 30, 0)
        mock_candidate.ai_suggestion_id = None

        # Mock query chain
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [mock_candidate]
        mock_db_session.query.return_value = mock_query

        response = test_client.get("/api/review")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "test-id-123"
        assert data[0]["title"] == "Test task"
        assert data[0]["ai_metadata"] is None

    def test_approve_candidate_not_found(
        self, test_client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Approving non-existent candidate should return error."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query

        response = test_client.post("/api/review/nonexistent-id/approve")

        assert response.status_code == 200
        data = response.json()
        assert data["error"] == "Not found"

    def test_approve_candidate_success(
        self, test_client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Approving valid candidate should create task."""
        # Create mock candidate
        mock_candidate = MagicMock()
        mock_candidate.id = "candidate-123"
        mock_candidate.title = "Test task"
        mock_candidate.description = "Test description"
        mock_candidate.raw_event_id = "event-456"
        mock_candidate.status = "pending"

        # Mock task after creation
        mock_task = MagicMock()
        mock_task.id = "task-789"

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_candidate
        mock_db_session.query.return_value = mock_query

        # Mock refresh to set task id
        def mock_refresh(obj):
            if hasattr(obj, "id") and obj.id is None:
                obj.id = "task-789"

        mock_db_session.refresh.side_effect = mock_refresh

        response = test_client.post("/api/review/candidate-123/approve")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert data["message"] == "Task created successfully"
        assert mock_candidate.status == "approved"

    def test_reject_candidate_not_found(
        self, test_client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Rejecting non-existent candidate should return error."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query

        response = test_client.post("/api/review/nonexistent-id/reject")

        assert response.status_code == 200
        data = response.json()
        assert data["error"] == "Not found"

    def test_reject_candidate_success(
        self, test_client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Rejecting valid candidate should update status."""
        mock_candidate = MagicMock()
        mock_candidate.id = "candidate-123"
        mock_candidate.raw_event_id = "event-456"
        mock_candidate.status = "pending"

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_candidate
        mock_db_session.query.return_value = mock_query

        response = test_client.post("/api/review/candidate-123/reject")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["candidate_id"] == "candidate-123"
        assert mock_candidate.status == "rejected"

    def test_get_recently_approved(
        self, test_client: TestClient, mock_db_session: MagicMock
    ) -> None:
        """Should return recently approved candidates."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query

        response = test_client.get("/api/review/approved")

        assert response.status_code == 200
        assert response.json() == []


class TestSlackIngestion:
    """Tests for /ingest/slack/events endpoint."""

    def test_slack_url_verification(self, test_client: TestClient) -> None:
        """Slack URL verification should return challenge."""
        response = test_client.post(
            "/ingest/slack/events",
            json={"type": "url_verification", "challenge": "test-challenge-123"},
        )

        assert response.status_code == 200
        assert response.json() == {"challenge": "test-challenge-123"}
