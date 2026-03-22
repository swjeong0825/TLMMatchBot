"""
Router for POST /parse-match.

Always returns HTTP 200 with a ParseMatchResponse.  The draft may be fully
resolved (missing_fields=[]) or partial (missing_fields lists the unresolved
slots).  The frontend is responsible for:

  1. Rendering the confirmation form with pre-filled values.
  2. Highlighting the slots listed in missing_fields so the player can fill them.
  3. Validating that all slots are non-null before forwarding to backend_main.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.schemas.parse_match_schemas import (
    ParseMatchRequest,
    ParseMatchResponse,
    PartialMatchDraft,
)
from app.dependencies import get_llm_provider
from app.llm.provider_interface import LLMProvider

router = APIRouter()


@router.post(
    "/parse-match",
    response_model=ParseMatchResponse,
    status_code=200,
    summary="Convert a natural-language match description into a (possibly partial) draft",
    description=(
        "Parses the player's free-text message and always returns HTTP 200 with a "
        "ParseMatchResponse.\n\n"
        "- **`missing_fields` is empty** → all four slots are resolved; the frontend "
        "shows the confirmation form and the player can submit to backend_main.\n\n"
        "- **`missing_fields` is non-empty** → one or more slots are `null`; the "
        "frontend highlights those fields so the player can fill them in before "
        "confirming.\n\n"
        "The `hint` string (when present) is the chatbot reply to display alongside "
        "the form when the parse is incomplete."
    ),
)
async def parse_match(
    body: ParseMatchRequest,
    provider: Annotated[LLMProvider, Depends(get_llm_provider)],
) -> JSONResponse:
    draft = await provider.parse_match_result(body.message)
    print(draft)

    response = ParseMatchResponse(
        league_id=body.league_id,
        raw_message=body.message,
        draft=PartialMatchDraft(
            team1_nicknames=draft.team1_nicknames,
            team2_nicknames=draft.team2_nicknames,
            team1_score=draft.team1_score,
            team2_score=draft.team2_score,
        ),
        missing_fields=draft.missing_fields,
        hint=draft.hint,
    )
    return JSONResponse(content=response.model_dump(), status_code=200)
