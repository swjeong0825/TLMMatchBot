"""
Groq provider stub.

To activate: set LLM_PROVIDER=groq in .env and supply GROQ_API_KEY.

Recommended implementation approach
-------------------------------------
1. Install:  pip install groq
2. Groq's API is OpenAI-compatible; use response_format={"type": "json_object"}
   together with an explicit system prompt instructing JSON output.
3. For stricter validation, consider using the `instructor` library on top of
   the Groq client, which handles retries and Pydantic parsing automatically.

Note on model choice
----------------------
Groq runs open-weight models (Llama, Mixtral) at very low latency.
llama3-8b-8192 is a good default for structured extraction tasks.
"""

from __future__ import annotations

import os
import json
from groq import AsyncGroq


from ..provider_interface import LLMProvider, MatchDraft

_SYSTEM_PROMPT = """
You are a tennis match result parser. Respond ONLY with a JSON object.

Extract from the user's message:
  - team1_nicknames: array of exactly 2 strings (first team mentioned)
  - team2_nicknames: array of exactly 2 strings (second team mentioned)
  - team1_score: score for team 1 as a non-negative integer string (e.g. "6")
  - team2_score: score for team 2 as a non-negative integer string (e.g. "3")
  - success: true if all fields resolved, false otherwise
  - error_code: "PARSE_INCOMPLETE" | "PARSE_AMBIGUOUS" (only when success=false)
  - error_message: string explaining what is missing (only when success=false)
  - missing_fields: array of unresolved field names (only when success=false)

Never invent player names. Scores are individual integers, not "X-Y" strings.
""".strip()


class GroqProvider(LLMProvider):
    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY")
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

        if not api_key:
            raise EnvironmentError("GROQ_API_KEY is not set in the environment.")

        # Uncomment once `groq` is installed:
        self._client = AsyncGroq(api_key=api_key)
        self._model = model
        # raise NotImplementedError(
        #     "GroqProvider is a stub. "
        #     "Install `groq`, uncomment the client, and implement parse_match_result."
        # )

    async def parse_match_result(self, message: str) -> MatchDraft:
        # --- Implementation sketch ---
        response = await self._client.chat.completions.create(
            model=self._model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": message},
            ],
        )
        data = json.loads(response.choices[0].message.content)
        if data.get("success"):
            return MatchDraft(
                team1_nicknames=data["team1_nicknames"],   # list[str | None], len 2
                team2_nicknames=data["team2_nicknames"],   # list[str | None], len 2
                team1_score=data.get("team1_score"),
                team2_score=data.get("team2_score"),
                missing_fields=[],
                hint=None,
            )
        return MatchDraft(
            team1_nicknames=data.get("team1_nicknames", [None, None]),
            team2_nicknames=data.get("team2_nicknames", [None, None]),
            team1_score=data.get("team1_score"),
            team2_score=data.get("team2_score"),
            missing_fields=data.get("missing_fields", []),
            hint=data.get("error_message"),
        )
        # raise NotImplementedError
