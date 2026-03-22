"""
Dependency injection: selects the active LLM provider from LLM_PROVIDER env var.

Supported values (case-insensitive):
  demo    → DemoProvider   (regex-based, no API key — default)
  openai  → OpenAIProvider (stub — install `openai` and set OPENAI_API_KEY)
  google  → GoogleProvider (stub — install `google-generativeai` and set GOOGLE_API_KEY)
  groq    → GroqProvider   (stub — install `groq` and set GROQ_API_KEY)

The provider is instantiated once at startup via @lru_cache so the same
instance is reused across requests (important for connection-pooled clients).
"""

from __future__ import annotations

import os
from functools import lru_cache

from app.llm.provider_interface import LLMProvider


@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProvider:
    provider_name = os.getenv("LLM_PROVIDER", "demo").lower().strip()

    if provider_name == "demo":
        from app.llm.demo_provider import DemoProvider
        return DemoProvider()

    if provider_name == "openai":
        from app.llm.providers.openai_provider import OpenAIProvider
        return OpenAIProvider()

    if provider_name == "google":
        from app.llm.providers.google_provider import GoogleProvider
        return GoogleProvider()

    if provider_name == "groq":
        from app.llm.providers.groq_provider import GroqProvider
        return GroqProvider()

    raise ValueError(
        f"Unknown LLM_PROVIDER '{provider_name}'. "
        "Valid values: demo, openai, google, groq."
    )
