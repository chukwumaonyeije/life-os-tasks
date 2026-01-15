"""
Unit tests for prompt engineering and PII redaction.
"""

from app.ai.prompts import (
    CURRENT_PROMPT_VERSION,
    PROMPT_V1,
    get_prompt,
    redact_pii,
    truncate_for_excerpt,
)


class TestRedactPii:
    """Tests for PII redaction function."""

    def test_redacts_ssn(self) -> None:
        """SSN pattern should be redacted."""
        text = "My SSN is 123-45-6789"
        result = redact_pii(text)
        assert "123-45-6789" not in result
        assert "[SSN-REDACTED]" in result

    def test_redacts_multiple_ssns(self) -> None:
        """Multiple SSNs should all be redacted."""
        text = "SSN1: 123-45-6789, SSN2: 987-65-4321"
        result = redact_pii(text)
        assert "123-45-6789" not in result
        assert "987-65-4321" not in result
        assert result.count("[SSN-REDACTED]") == 2

    def test_redacts_credit_card_no_separators(self) -> None:
        """Credit card without separators should be redacted."""
        text = "Card: 1234567890123456"
        result = redact_pii(text)
        assert "1234567890123456" not in result
        assert "[CC-REDACTED]" in result

    def test_redacts_credit_card_with_spaces(self) -> None:
        """Credit card with spaces should be redacted."""
        text = "Card: 1234 5678 9012 3456"
        result = redact_pii(text)
        assert "1234 5678 9012 3456" not in result
        assert "[CC-REDACTED]" in result

    def test_redacts_credit_card_with_dashes(self) -> None:
        """Credit card with dashes should be redacted."""
        text = "Card: 1234-5678-9012-3456"
        result = redact_pii(text)
        assert "1234-5678-9012-3456" not in result
        assert "[CC-REDACTED]" in result

    def test_redacts_email(self) -> None:
        """Email addresses should be redacted."""
        text = "Contact me at john.doe@example.com"
        result = redact_pii(text)
        assert "john.doe@example.com" not in result
        assert "[EMAIL-REDACTED]" in result

    def test_redacts_various_email_formats(self) -> None:
        """Various email formats should be redacted."""
        emails = [
            "simple@example.com",
            "very.common@example.com",
            "user+tag@example.org",
            "user_name@example.co.uk",
        ]
        for email in emails:
            text = f"Email: {email}"
            result = redact_pii(text)
            assert email not in result
            assert "[EMAIL-REDACTED]" in result

    def test_redacts_phone_standard_format(self) -> None:
        """Standard phone format (XXX-XXX-XXXX) should be redacted."""
        text = "Call me at 555-123-4567"
        result = redact_pii(text)
        assert "555-123-4567" not in result
        assert "[PHONE-REDACTED]" in result

    def test_redacts_phone_with_parentheses(self) -> None:
        """Phone with parentheses should be redacted."""
        text = "Call me at (555) 123-4567"
        result = redact_pii(text)
        assert "(555) 123-4567" not in result
        assert "[PHONE-REDACTED]" in result

    def test_redacts_phone_with_dots(self) -> None:
        """Phone with dots should be redacted."""
        text = "Call me at 555.123.4567"
        result = redact_pii(text)
        assert "555.123.4567" not in result
        assert "[PHONE-REDACTED]" in result

    def test_redacts_phone_no_separators(self) -> None:
        """Phone without separators should be redacted."""
        text = "Call me at 5551234567"
        result = redact_pii(text)
        assert "5551234567" not in result
        assert "[PHONE-REDACTED]" in result

    def test_redacts_phone_with_country_code(self) -> None:
        """Phone with +1 country code should be redacted."""
        text = "Call me at +1-555-123-4567"
        result = redact_pii(text)
        assert "555-123-4567" not in result
        assert "[PHONE-REDACTED]" in result

    def test_preserves_non_pii_text(self) -> None:
        """Non-PII text should be preserved."""
        text = "Schedule a meeting with the team tomorrow at 3pm"
        result = redact_pii(text)
        assert result == text

    def test_handles_mixed_pii(self) -> None:
        """Multiple types of PII should all be redacted."""
        text = "Contact John at john@example.com or 555-123-4567. SSN: 123-45-6789"
        result = redact_pii(text)
        assert "[EMAIL-REDACTED]" in result
        assert "[PHONE-REDACTED]" in result
        assert "[SSN-REDACTED]" in result
        assert "Contact John at" in result

    def test_handles_empty_string(self) -> None:
        """Empty string should return empty string."""
        result = redact_pii("")
        assert result == ""

    def test_preserves_partial_matches(self) -> None:
        """Partial patterns should not be redacted."""
        text = "The code is 12-34-567"  # Not a valid SSN
        result = redact_pii(text)
        assert result == text


class TestGetPrompt:
    """Tests for get_prompt function."""

    def test_returns_v1_prompt(self) -> None:
        """Should return v1 prompt when requested."""
        result = get_prompt("v1")
        assert result == PROMPT_V1

    def test_default_returns_current_version(self) -> None:
        """Default should return current prompt version."""
        result = get_prompt()
        assert result == get_prompt(CURRENT_PROMPT_VERSION)

    def test_unknown_version_returns_v1(self) -> None:
        """Unknown version should fall back to v1."""
        result = get_prompt("v999")
        assert result == PROMPT_V1

    def test_prompt_contains_placeholder(self) -> None:
        """Prompt should contain {text} placeholder."""
        result = get_prompt()
        assert "{text}" in result

    def test_prompt_contains_json_format(self) -> None:
        """Prompt should describe JSON format."""
        result = get_prompt()
        assert "JSON" in result
        assert "title" in result
        assert "priority" in result
        assert "confidence" in result


class TestTruncateForExcerpt:
    """Tests for truncate_for_excerpt function."""

    def test_short_text_unchanged(self) -> None:
        """Text under max_length should be unchanged."""
        text = "Short text"
        result = truncate_for_excerpt(text, max_length=500)
        assert result == text

    def test_long_text_truncated(self) -> None:
        """Long text should be truncated with ellipsis."""
        text = "A" * 600
        result = truncate_for_excerpt(text, max_length=500)
        assert len(result) == 500
        assert result.endswith("...")

    def test_exact_length_unchanged(self) -> None:
        """Text at exactly max_length should be unchanged."""
        text = "A" * 500
        result = truncate_for_excerpt(text, max_length=500)
        assert result == text
        assert len(result) == 500

    def test_custom_max_length(self) -> None:
        """Custom max_length should be respected."""
        text = "A" * 100
        result = truncate_for_excerpt(text, max_length=50)
        assert len(result) == 50
        assert result.endswith("...")

    def test_default_max_length_is_500(self) -> None:
        """Default max_length should be 500."""
        text = "A" * 600
        result = truncate_for_excerpt(text)
        assert len(result) == 500
