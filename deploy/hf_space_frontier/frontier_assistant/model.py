"""Frontier model backend via Groq (free tier, OpenAI-compatible API)."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from shared.groq_client import DEFAULT_GROQ_MODEL, chat_completion
from shared.prompts import SYSTEM_PROMPT

load_dotenv()


class FrontierModel:
    def __init__(self, model_id: str | None = None):
        self.provider = "groq"
        self.model_id = model_id or os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)

    def generate(self, messages: list[dict[str, str]], max_tokens: int = 1024) -> str:
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}, *messages]
        return chat_completion(
            messages=api_messages,
            model=self.model_id,
            max_tokens=max_tokens,
            temperature=0.7,
        )


_model_instance: FrontierModel | None = None


def get_model() -> FrontierModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = FrontierModel()
    return _model_instance
