"""
Unit tests for AI provider factory.
"""

import os
from unittest.mock import patch


class TestGetSuggester:
    """Tests for get_suggester factory function."""

    def test_returns_none_when_disabled(self) -> None:
        """Should return None when AI_PROVIDER=none."""
        with patch.dict(os.environ, {"AI_PROVIDER": "none"}):
            from app.ai.factory import get_suggester

            result = get_suggester()
            assert result is None

    def test_returns_none_when_not_set(self) -> None:
        """Should return None when AI_PROVIDER not set."""
        env = os.environ.copy()
        env.pop("AI_PROVIDER", None)

        with patch.dict(os.environ, env, clear=True):
            # Need to reload module to pick up env change
            from importlib import reload

            import app.ai.factory

            reload(app.ai.factory)
            result = app.ai.factory.get_suggester()
            assert result is None

    def test_returns_none_for_unknown_provider(self) -> None:
        """Should return None for unknown provider."""
        with patch.dict(os.environ, {"AI_PROVIDER": "unknown_provider"}):
            from importlib import reload

            import app.ai.factory

            reload(app.ai.factory)
            result = app.ai.factory.get_suggester()
            assert result is None

    def test_openai_provider_without_package(self) -> None:
        """Should return None when OpenAI package not installed."""
        with patch.dict(os.environ, {"AI_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"}):
            with patch.dict("sys.modules", {"openai": None}):
                from importlib import reload

                import app.ai.factory

                reload(app.ai.factory)

                # Mock the import to raise ImportError
                with patch(
                    "app.ai.providers.openai_suggester.OpenAISuggester",
                    side_effect=ImportError("No module named 'openai'"),
                ):
                    result = app.ai.factory.get_suggester()
                    assert result is None

    def test_anthropic_provider_without_package(self) -> None:
        """Should return None when Anthropic package not installed."""
        with patch.dict(os.environ, {"AI_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "test-key"}):
            from importlib import reload

            import app.ai.factory

            reload(app.ai.factory)

            # Mock the import to raise ImportError
            with patch(
                "app.ai.providers.claude_suggester.ClaudeSuggester",
                side_effect=ImportError("No module named 'anthropic'"),
            ):
                result = app.ai.factory.get_suggester()
                assert result is None

    def test_provider_case_insensitive(self) -> None:
        """Provider name should be case insensitive."""
        for provider in ["NONE", "None", "NoNe"]:
            with patch.dict(os.environ, {"AI_PROVIDER": provider}):
                from importlib import reload

                import app.ai.factory

                reload(app.ai.factory)
                result = app.ai.factory.get_suggester()
                assert result is None

    def test_openai_missing_api_key(self) -> None:
        """Should handle missing OpenAI API key gracefully."""
        env = {"AI_PROVIDER": "openai"}
        # Remove API key if present
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("OPENAI_API_KEY", None)

            from importlib import reload

            import app.ai.factory

            reload(app.ai.factory)

            # This should raise ValueError from OpenAISuggester
            with patch(
                "app.ai.providers.openai_suggester.OpenAISuggester",
                side_effect=ValueError("OPENAI_API_KEY not set"),
            ):
                result = app.ai.factory.get_suggester()
                assert result is None

    def test_anthropic_missing_api_key(self) -> None:
        """Should handle missing Anthropic API key gracefully."""
        env = {"AI_PROVIDER": "anthropic"}
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("ANTHROPIC_API_KEY", None)

            from importlib import reload

            import app.ai.factory

            reload(app.ai.factory)

            # This should raise ValueError from ClaudeSuggester
            with patch(
                "app.ai.providers.claude_suggester.ClaudeSuggester",
                side_effect=ValueError("ANTHROPIC_API_KEY not set"),
            ):
                result = app.ai.factory.get_suggester()
                assert result is None
