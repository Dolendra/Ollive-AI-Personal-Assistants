"""Groq API client (OpenAI-compatible). Used for frontier assistant and eval judge."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
DEFAULT_JUDGE_MODEL = os.getenv("JUDGE_MODEL", DEFAULT_GROQ_MODEL)


def get_groq_client():
    from openai import OpenAI

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Get a free key at https://console.groq.com/keys"
        )
    return OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)


def chat_completion(
    *,
    messages: list[dict[str, str]],
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    client = get_groq_client()
    resp = client.chat.completions.create(
        model=model or DEFAULT_GROQ_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""
