"""
Demo LLM provider — regex-based, no API key required.

Handles the most common English match-description patterns:

  Win  : "Alice and Bob beat Charlie and Dave 6-3"
         "Alice and Bob defeated Charlie and Dave 6-3"
         "Alice and Bob won against Charlie and Dave 6-3"
  Loss : "Alice and Bob lost to Charlie and Dave 3-6"
         "Alice and Bob were beaten by Charlie and Dave 3-6"
  Neutral: "Alice and Bob vs Charlie and Dave 7-5"

Score convention: the first integer in "X-Y" is always treated as team1's
score and the second as team2's, regardless of who won — unless a "loss verb"
is present, in which case the scores are swapped so team1_score always
belongs to the first team mentioned.

Partial extraction: if fewer than 4 player names or no score can be found,
the draft is returned with the resolved slots filled and unresolved slots set
to None.  missing_fields reports slot-level identifiers ("team1_nicknames[1]",
"team2_score", etc.) so the frontend can highlight the exact input boxes.
"""

from __future__ import annotations

import re
from typing import Final

from .provider_interface import LLMProvider, MatchDraft


# ---------------------------------------------------------------------------
# Regex constants
# ---------------------------------------------------------------------------

_SCORE_RE: Final = re.compile(r"\b(\d+)\s*[-–]\s*(\d+)\b")

_LOSS_VERB_RE: Final = re.compile(
    r"\b(?:lost\s+to|were\s+beaten\s+by|were\s+defeated\s+by|got\s+beaten\s+by)\b",
    re.IGNORECASE,
)

_NOISE_WORDS: Final = frozenset(
    {"And", "Vs", "Versus", "Beat", "Beats", "Defeated", "Lost", "Won", "Against"}
)

_NAME_TOKEN_RE: Final = re.compile(r"\b([A-Z][a-zA-Z'-]+)\b")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_unique_names(message: str) -> list[str]:
    """Return capitalised name tokens in order, de-duplicated, noise-filtered."""
    seen: set[str] = set()
    unique: list[str] = []
    for tok in _NAME_TOKEN_RE.findall(message):
        if tok in _NOISE_WORDS:
            continue
        key = tok.lower()
        if key not in seen:
            seen.add(key)
            unique.append(tok)
    return unique


def _slot(names: list[str], index: int) -> str | None:
    """Return names[index] or None if the index is out of range."""
    return names[index] if index < len(names) else None


def _build_hint(missing: list[str]) -> str | None:
    if not missing:
        return None
    readable = []
    for f in missing:
        if f.startswith("team1_nicknames"):
            slot = f[len("team1_nicknames"):]          # "[0]" or "[1]"
            readable.append(f"team 1 player {slot[1]}")
        elif f.startswith("team2_nicknames"):
            slot = f[len("team2_nicknames"):]
            readable.append(f"team 2 player {slot[1]}")
        elif f == "team1_score":
            readable.append("team 1 score")
        elif f == "team2_score":
            readable.append("team 2 score")
        else:
            readable.append(f.replace("_", " "))
    joined = ", ".join(readable)
    return (
        f"I couldn't extract {joined} from your message. "
        "Please fill in the highlighted fields below."
    )


# ---------------------------------------------------------------------------
# Provider implementation
# ---------------------------------------------------------------------------


class DemoProvider(LLMProvider):
    """
    Rule-based demo provider.  Swap for a real LLM provider by setting
    LLM_PROVIDER=openai (or google / groq) in .env.
    """

    async def parse_match_result(self, message: str) -> MatchDraft:
        # ── Score extraction ─────────────────────────────────────────────
        score_match = _SCORE_RE.search(message)
        if score_match is None:
            team1_score: str | None = None
            team2_score: str | None = None
        else:
            raw1, raw2 = score_match.group(1), score_match.group(2)
            if _LOSS_VERB_RE.search(message):
                team1_score, team2_score = raw2, raw1   # first team is the loser
            else:
                team1_score, team2_score = raw1, raw2

        # ── Name extraction ──────────────────────────────────────────────
        names = _extract_unique_names(message)

        team1: list[str | None] = [_slot(names, 0), _slot(names, 1)]
        team2: list[str | None] = [_slot(names, 2), _slot(names, 3)]

        # ── Slot-level missing_fields ────────────────────────────────────
        missing: list[str] = []
        for i, v in enumerate(team1):
            if v is None:
                missing.append(f"team1_nicknames[{i}]")
        for i, v in enumerate(team2):
            if v is None:
                missing.append(f"team2_nicknames[{i}]")
        if team1_score is None:
            missing.append("team1_score")
        if team2_score is None:
            missing.append("team2_score")

        return MatchDraft(
            team1_nicknames=team1,
            team2_nicknames=team2,
            team1_score=team1_score,
            team2_score=team2_score,
            missing_fields=missing,
            hint=_build_hint(missing),
        )
