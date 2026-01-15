"""
Unit tests for AI contract validation.
"""

from app.ai.contract import AISuggestion, suggestion_to_dict, validate_suggestion


class TestValidateSuggestion:
    """Tests for validate_suggestion function."""

    def test_valid_suggestion(self, valid_suggestion_data: dict) -> None:
        """Valid data should return AISuggestion instance."""
        result = validate_suggestion(valid_suggestion_data)

        assert result is not None
        assert isinstance(result, AISuggestion)
        assert result.title == "Schedule team meeting"
        assert result.description == "Set up weekly sync with the development team"
        assert result.priority == "medium"
        assert result.confidence == 0.85
        assert result.rationale == "The text mentions needing to coordinate with team members"

    def test_empty_title_returns_none(self, invalid_suggestion_data_empty_title: dict) -> None:
        """Empty title should return None."""
        result = validate_suggestion(invalid_suggestion_data_empty_title)
        assert result is None

    def test_whitespace_only_title_returns_none(self) -> None:
        """Whitespace-only title should return None."""
        data = {
            "title": "   ",
            "description": "Some description",
            "priority": "medium",
            "confidence": 0.5,
            "rationale": "Some rationale",
        }
        result = validate_suggestion(data)
        assert result is None

    def test_long_title_returns_none(self, invalid_suggestion_data_long_title: dict) -> None:
        """Title exceeding 60 chars should return None."""
        result = validate_suggestion(invalid_suggestion_data_long_title)
        assert result is None

    def test_title_exactly_60_chars_is_valid(self) -> None:
        """Title with exactly 60 chars should be valid."""
        data = {
            "title": "A" * 60,
            "description": "Some description",
            "priority": "medium",
            "confidence": 0.5,
            "rationale": "Some rationale",
        }
        result = validate_suggestion(data)
        assert result is not None
        assert len(result.title) == 60

    def test_invalid_priority_returns_none(
        self, invalid_suggestion_data_bad_priority: dict
    ) -> None:
        """Invalid priority should return None."""
        result = validate_suggestion(invalid_suggestion_data_bad_priority)
        assert result is None

    def test_valid_priorities(self) -> None:
        """All valid priority values should be accepted."""
        for priority in ["low", "medium", "high"]:
            data = {
                "title": "Valid title",
                "description": "Some description",
                "priority": priority,
                "confidence": 0.5,
                "rationale": "Some rationale",
            }
            result = validate_suggestion(data)
            assert result is not None
            assert result.priority == priority

    def test_confidence_too_high_returns_none(
        self, invalid_suggestion_data_bad_confidence: dict
    ) -> None:
        """Confidence > 1.0 should return None."""
        result = validate_suggestion(invalid_suggestion_data_bad_confidence)
        assert result is None

    def test_confidence_negative_returns_none(self) -> None:
        """Negative confidence should return None."""
        data = {
            "title": "Valid title",
            "description": "Some description",
            "priority": "medium",
            "confidence": -0.1,
            "rationale": "Some rationale",
        }
        result = validate_suggestion(data)
        assert result is None

    def test_confidence_boundary_values(self) -> None:
        """Confidence at 0.0 and 1.0 should be valid."""
        for confidence in [0.0, 1.0]:
            data = {
                "title": "Valid title",
                "description": "Some description",
                "priority": "medium",
                "confidence": confidence,
                "rationale": "Some rationale",
            }
            result = validate_suggestion(data)
            assert result is not None
            assert result.confidence == confidence

    def test_confidence_as_string_number(self) -> None:
        """Confidence as string number should be converted."""
        data = {
            "title": "Valid title",
            "description": "Some description",
            "priority": "medium",
            "confidence": "0.75",
            "rationale": "Some rationale",
        }
        result = validate_suggestion(data)
        assert result is not None
        assert result.confidence == 0.75

    def test_confidence_as_invalid_string_returns_none(self) -> None:
        """Non-numeric confidence string should return None."""
        data = {
            "title": "Valid title",
            "description": "Some description",
            "priority": "medium",
            "confidence": "not a number",
            "rationale": "Some rationale",
        }
        result = validate_suggestion(data)
        assert result is None

    def test_missing_optional_fields_use_defaults(self) -> None:
        """Missing description and rationale should use empty strings."""
        data = {
            "title": "Valid title",
            "priority": "high",
            "confidence": 0.9,
        }
        result = validate_suggestion(data)
        assert result is not None
        assert result.description == ""
        assert result.rationale == ""

    def test_missing_priority_uses_default(self) -> None:
        """Missing priority should default to 'medium'."""
        data = {
            "title": "Valid title",
            "confidence": 0.5,
        }
        result = validate_suggestion(data)
        assert result is not None
        assert result.priority == "medium"

    def test_missing_confidence_uses_default(self) -> None:
        """Missing confidence should default to 0.0."""
        data = {
            "title": "Valid title",
            "priority": "low",
        }
        result = validate_suggestion(data)
        assert result is not None
        assert result.confidence == 0.0

    def test_non_dict_input_returns_none(self) -> None:
        """Non-dict input should return None."""
        assert validate_suggestion("not a dict") is None
        assert validate_suggestion(["list"]) is None
        assert validate_suggestion(None) is None
        assert validate_suggestion(123) is None

    def test_missing_title_returns_none(self) -> None:
        """Missing title field should return None."""
        data = {
            "description": "Some description",
            "priority": "medium",
            "confidence": 0.5,
        }
        result = validate_suggestion(data)
        assert result is None


class TestSuggestionToDict:
    """Tests for suggestion_to_dict function."""

    def test_converts_suggestion_to_dict(self) -> None:
        """AISuggestion should convert to dict correctly."""
        suggestion = AISuggestion(
            title="Test task",
            description="Test description",
            priority="high",
            confidence=0.95,
            rationale="Test rationale",
        )

        result = suggestion_to_dict(suggestion)

        assert isinstance(result, dict)
        assert result["title"] == "Test task"
        assert result["description"] == "Test description"
        assert result["priority"] == "high"
        assert result["confidence"] == 0.95
        assert result["rationale"] == "Test rationale"

    def test_roundtrip_conversion(self, valid_suggestion_data: dict) -> None:
        """Validate -> to_dict should preserve data."""
        suggestion = validate_suggestion(valid_suggestion_data)
        assert suggestion is not None

        result = suggestion_to_dict(suggestion)

        assert result["title"] == valid_suggestion_data["title"]
        assert result["description"] == valid_suggestion_data["description"]
        assert result["priority"] == valid_suggestion_data["priority"]
        assert result["confidence"] == valid_suggestion_data["confidence"]
        assert result["rationale"] == valid_suggestion_data["rationale"]
