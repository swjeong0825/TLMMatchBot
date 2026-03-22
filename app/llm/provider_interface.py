"""
Abstract LLM provider interface.

Every concrete provider (Demo, OpenAI, Google, Groq …) must implement
LLMProvider.parse_match_result.  The method always returns a MatchDraft —
a unified result type that can represent both fully-resolved and partial
parses via nullable fields and a missing_fields list.

Partial draft contract
-----------------------
- team1_nicknames and team2_nicknames are always lists of exactly 2 slots.
  A slot is None when the provider could not confidently extract that player.
  Example: ["Alice", None] means only the first player was identified.
- team1_score / team2_score are None when the score could not be extracted.
- missing_fields lists the specific unresolved slots using dot/bracket notation
  so the frontend can highlight the exact input boxes:
    "team1_nicknames[1]", "team2_nicknames[0]", "team1_score", …
- hint is an optional human-readable message the chatbot UI should show the
  player when missing_fields is non-empty, prompting them to fill the gaps.
- When missing_fields is empty the draft is fully resolved and ready to be
  forwarded to backend_main after the player confirms.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass
class MatchDraft:
    """
    Unified parse result — always returned by the provider regardless of
    whether the parse is complete or partial.

    Field names and semantics mirror SubmitMatchResultRequest on backend_main
    (POST /leagues/{league_id}/matches), except individual slots may be None
    when the provider could not extract them.
    """

    team1_nicknames: list[str | None]  # exactly 2 slots; None = not extracted
    team2_nicknames: list[str | None]  # exactly 2 slots; None = not extracted
    team1_score: str | None            # non-negative integer string or None
    team2_score: str | None            # non-negative integer string or None
    missing_fields: list[str] = field(default_factory=list)
    hint: str | None = None            # chatbot reply when parse is incomplete

    @property
    def is_complete(self) -> bool:
        return len(self.missing_fields) == 0


# ---------------------------------------------------------------------------
# Abstract provider
# ---------------------------------------------------------------------------


class LLMProvider(ABC):
    """
    One method contract every provider must satisfy.

    Implementors should:
      - Always return a MatchDraft — never raise.
      - Populate missing_fields with slot-level identifiers for each None value.
      - Set hint to a player-facing message when missing_fields is non-empty.
      - For ambiguous parses, use the best-guess values for resolved slots and
        leave genuinely ambiguous slots as None.
    """

    @abstractmethod
    async def parse_match_result(self, message: str) -> MatchDraft:
        """Convert a free-text match description into a (possibly partial) MatchDraft."""
        ...
