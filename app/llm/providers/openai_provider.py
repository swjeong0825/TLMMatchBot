"""
OpenAI provider stub.

To activate: set LLM_PROVIDER=openai in .env and supply OPENAI_API_KEY.

Recommended implementation approach
-------------------------------------
1. Install:  pip install openai
2. Use structured outputs (json_schema / response_format) so the model
   returns a JSON object that maps directly to MatchDraft.
3. System prompt should instruct the model to:
   - Extract exactly two nicknames per team.
   - Return scores as non-negative integer strings (e.g. "6", not "6-3").
   - Set error_code to PARSE_INCOMPLETE when names or score are absent.
   - Set error_code to PARSE_AMBIGUOUS when multiple interpretations exist.

Example response_format schema
---------------------------------
{
  "type": "json_schema",
  "json_schema": {
    "name": "match_parse_result",
    "strict": true,
    "schema": {
      "type": "object",
      "properties": {
        "success": { "type": "boolean" },
        "team1_nicknames": { "type": "array", "items": { "type": "string" } },
        "team2_nicknames": { "type": "array", "items": { "type": "string" } },
        "team1_score":     { "type": "string" },
        "team2_score":     { "type": "string" },
        "error_code":      { "type": "string", "enum": ["PARSE_INCOMPLETE", "PARSE_AMBIGUOUS"] },
        "error_message":   { "type": "string" },
        "missing_fields":  { "type": "array", "items": { "type": "string" } }
      },
      "required": ["success"],
      "additionalProperties": false
    }
  }
}
"""

from __future__ import annotations

import os

from ..provider_interface import LLMProvider, MatchDraft

_SYSTEM_PROMPT = """
You are a tennis match result parser.
Given a free-text match description, extract:
  - team1_nicknames: list of exactly 2 player nicknames (the first team mentioned)
  - team2_nicknames: list of exactly 2 player nicknames (the second team mentioned)
  - team1_score: score for team 1 as a non-negative integer string (e.g. "6")
  - team2_score: score for team 2 as a non-negative integer string (e.g. "3")

Rules:
  - Normalise nicknames to their original capitalisation from the message.
  - Scores must be single integers, not ranges like "6-3" — extract per-team.
  - If you cannot confidently extract all fields, set success=false and
    populate error_code, error_message, and missing_fields.
  - Never invent or hallucinate player names.
""".strip()


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY is not set in the environment.")

        # Uncomment once `openai` is installed:
        # from openai import AsyncOpenAI
        # self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        raise NotImplementedError(
            "OpenAIProvider is a stub. "
            "Install `openai`, uncomment the client, and implement parse_match_result."
        )

    async def parse_match_result(self, message: str) -> MatchDraft:
        # --- Implementation sketch ---
        # response = await self._client.chat.completions.create(
        #     model=self._model,
        #     response_format=<json_schema from module docstring>,
        #     messages=[
        #         {"role": "system", "content": _SYSTEM_PROMPT},
        #         {"role": "user",   "content": message},
        #     ],
        # )
        # data = json.loads(response.choices[0].message.content)
        # if data["success"]:
        #     return MatchDraft(
        #         team1_nicknames=data["team1_nicknames"],   # list[str | None], len 2
        #         team2_nicknames=data["team2_nicknames"],   # list[str | None], len 2
        #         team1_score=data.get("team1_score"),       # str | None
        #         team2_score=data.get("team2_score"),       # str | None
        #         missing_fields=[],
        #         hint=None,
        #     )
        # return MatchDraft(
        #     team1_nicknames=data.get("team1_nicknames", [None, None]),
        #     team2_nicknames=data.get("team2_nicknames", [None, None]),
        #     team1_score=data.get("team1_score"),
        #     team2_score=data.get("team2_score"),
        #     missing_fields=data.get("missing_fields", []),
        #     hint=data.get("error_message"),
        # )
        raise NotImplementedError
