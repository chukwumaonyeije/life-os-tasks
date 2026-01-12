"""
AI Suggestion Engine: Advisory-only task extraction.

This module provides AI-powered task suggestion capabilities while
maintaining human authority over all task creation decisions.

Key Principles:
- Subordination: AI suggests, humans decide
- Replaceability: Providers are swappable
- Failure Safety: System works without AI
- Auditability: All suggestions are traceable
"""

from app.ai.contract import AISuggestion, validate_suggestion, suggestion_to_dict

__all__ = ['AISuggestion', 'validate_suggestion', 'suggestion_to_dict']
