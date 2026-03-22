"""
FastAPI application entry point for the LLM backend.

This service exposes one endpoint:
  POST /parse-match
    Accepts a free-text match description and returns a structured draft
    matching the SubmitMatchResultRequest shape of backend_main, ready for
    the player to review on the frontend confirmation form.

Start with:
  uvicorn app.main:app --reload --port 8001
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.parse_match_router import router as parse_match_router
from app.dependencies import get_llm_provider

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Eagerly instantiate and validate the provider at startup so a
    # misconfigured API key fails fast rather than on the first request.
    get_llm_provider()
    yield


app = FastAPI(
    title="Tennis League Chatbot — LLM Backend",
    description=(
        "Accepts a free-text chat message describing a doubles match result, "
        "parses it with the configured LLM provider, and returns a structured "
        "draft for the frontend confirmation step.\n\n"
        "Set **LLM_PROVIDER** in `.env` to switch providers: "
        "`demo` (default) | `openai` | `google` | `groq`."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten for production
    allow_methods=["POST"],
    allow_headers=["*"],
)

app.include_router(parse_match_router)
