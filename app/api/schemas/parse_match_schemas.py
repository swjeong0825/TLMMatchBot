"""
Pydantic request/response schemas for POST /parse-match.

Key design decision: the response uses PartialMatchDraft (nullable slots)
instead of the strict SubmitMatchResultDraft.  This lets the frontend render
a confirmation form with pre-filled fields and highlighted empty boxes for
the player to complete, rather than forcing them to retype everything when
the parse is only partially successful.

When missing_fields is empty the draft is fully resolved and the frontend can
forward it directly to backend_main after the player confirms.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------


class ParseMatchRequest(BaseModel):
    league_id: str = Field(
        description=(
            "UUID of the league this match belongs to. "
            "Echoed in the response so the frontend can build the backend_main URL."
        ),
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    message: Annotated[str, Field(min_length=1)] = Field(
        description=(
            "Free-text match description entered by the player. "
            "Example: 'Alice and Bob beat Charlie and Dave 6-3'"
        ),
        examples=["Alice and Bob beat Charlie and Dave 6-3"],
    )


# ---------------------------------------------------------------------------
# Partial draft — backend_llm response; individual slots may be None
# ---------------------------------------------------------------------------


class PartialMatchDraft(BaseModel):
    """
    Draft with nullable slots returned by backend_llm.

    team1_nicknames and team2_nicknames always contain exactly 2 elements;
    a None element means the provider could not extract that player.

    After the player fills every None slot and confirms, the frontend sends
    the completed values to backend_main's POST /leagues/{league_id}/matches.
    backend_main enforces the no-null constraint and score validation.
    """

    team1_nicknames: list[str | None] = Field(
        description="Exactly 2 slots for team 1; None = player not extracted.",
        examples=[["Alice", "Bob"]],
    )
    team2_nicknames: list[str | None] = Field(
        description="Exactly 2 slots for team 2; None = player not extracted.",
        examples=[["Charlie", None]],
    )
    team1_score: str | None = Field(
        default=None,
        description="Score for team 1 (non-negative integer string) or null if not extracted.",
        examples=["6"],
    )
    team2_score: str | None = Field(
        default=None,
        description="Score for team 2 (non-negative integer string) or null if not extracted.",
        examples=["3"],
    )

    @model_validator(mode="after")
    def nicknames_must_have_two_slots(self) -> "PartialMatchDraft":
        if len(self.team1_nicknames) != 2:
            raise ValueError("team1_nicknames must have exactly 2 slots")
        if len(self.team2_nicknames) != 2:
            raise ValueError("team2_nicknames must have exactly 2 slots")
        return self


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------


class ParseMatchResponse(BaseModel):
    league_id: str = Field(
        description="Echoed from the request; used by the frontend to build the backend_main URL.",
    )
    raw_message: str = Field(
        description="The original player message, echoed back for display alongside the form.",
    )
    draft: PartialMatchDraft
    missing_fields: list[str] = Field(
        default_factory=list,
        description=(
            "Slot-level identifiers for every None value in the draft. "
            "Empty list means the parse is complete and the draft is ready to confirm. "
            "Format: 'team1_nicknames[0]', 'team1_nicknames[1]', "
            "'team2_nicknames[0]', 'team2_nicknames[1]', 'team1_score', 'team2_score'."
        ),
        examples=[["team2_nicknames[1]", "team1_score", "team2_score"]],
    )
    hint: str | None = Field(
        default=None,
        description=(
            "Optional chatbot reply to display when missing_fields is non-empty. "
            "Prompts the player to fill in the highlighted slots."
        ),
    )
