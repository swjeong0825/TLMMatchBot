"""
Google Gemini provider stub.

To activate: set LLM_PROVIDER=google in .env and supply GOOGLE_API_KEY.

Recommended implementation approach
-------------------------------------
1. Install:  pip install google-generativeai
2. Use generate_content with response_mime_type="application/json" and a
   response_schema (Pydantic-style or TypedDict) to enforce structured output.
3. The same system prompt and JSON schema described in openai_provider.py
   work equally well here.

Key difference from OpenAI
-----------------------------
Gemini's structured output is requested via GenerationConfig:
  generation_config = genai.GenerationConfig(
      response_mime_type="application/json",
      response_schema=<your schema>,
  )
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
  - Scores must be single integers — extract per-team.
  - If you cannot confidently extract all fields, set success=false and
    populate error_code, error_message, and missing_fields.
  - Never invent or hallucinate player names.
""".strip()


class GoogleProvider(LLMProvider):
    def __init__(self) -> None:
        api_key = os.getenv("GOOGLE_API_KEY")
        model = os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")

        if not api_key:
            raise EnvironmentError("GOOGLE_API_KEY is not set in the environment.")

        # Uncomment once `google-generativeai` is installed:
        # import google.generativeai as genai
        # genai.configure(api_key=api_key)
        # self._model = genai.GenerativeModel(model, system_instruction=_SYSTEM_PROMPT)
        self._model_name = model
        raise NotImplementedError(
            "GoogleProvider is a stub. "
            "Install `google-generativeai`, uncomment the client, and implement parse_match_result."
        )

    async def parse_match_result(self, message: str) -> MatchDraft:
        # --- Implementation sketch ---
        # import asyncio, json
        # response = await asyncio.to_thread(
        #     self._model.generate_content,
        #     message,
        #     generation_config=genai.GenerationConfig(
        #         response_mime_type="application/json",
        #     ),
        # )
        # data = json.loads(response.text)
        # if data["success"]:
        #     return MatchDraft(
        #         team1_nicknames=data["team1_nicknames"],   # list[str | None], len 2
        #         team2_nicknames=data["team2_nicknames"],   # list[str | None], len 2
        #         team1_score=data.get("team1_score"),
        #         team2_score=data.get("team2_score"),
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
