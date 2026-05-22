"""Frontier assistant orchestration."""

from __future__ import annotations

from shared.guardrails import check_input, sanitize_output
from shared.tools import maybe_run_tools
from shared.memory import ConversationMemory
from shared.observability import log_interaction, track_latency
from shared.prompts import REFUSAL_MESSAGE, build_chat_messages

from frontier_assistant.model import get_model


class FrontierAssistant:
    def __init__(self):
        self.memory = ConversationMemory()
        self.model = get_model()

    def chat(self, user_message: str, history: list[tuple[str, str]]) -> tuple[str, list[tuple[str, str]]]:
        guard = check_input(user_message)
        if guard.blocked and guard.category != "bias_probe":
            reply = guard.reason or REFUSAL_MESSAGE
            history = history + [(user_message, reply)]
            log_interaction(
                assistant_type="frontier",
                user_message=user_message,
                assistant_response=reply,
                latency_ms=0,
                blocked=True,
                guardrail_category=guard.category,
                model_id=f"{self.model.provider}:{self.model.model_id}",
            )
            return "", history

        tool_note = maybe_run_tools(user_message)
        enriched = user_message
        if tool_note:
            enriched = f"{user_message}\n\n{tool_note}"
        messages = build_chat_messages(history, enriched)

        with track_latency():
            try:
                raw = self.model.generate(messages)
            except Exception as exc:
                raw = (
                    f"I encountered an API error: {exc}. "
                    "Check GROQ_API_KEY in your .env file (https://console.groq.com/keys)."
                )

        reply = sanitize_output(raw)
        history = history + [(user_message, reply)]

        log_interaction(
            assistant_type="frontier",
            user_message=user_message,
            assistant_response=reply,
            latency_ms=track_latency.last_ms,
            blocked=False,
            guardrail_category=guard.category,
            model_id=f"{self.model.provider}:{self.model.model_id}",
        )
        return "", history

    def clear(self) -> list:
        self.memory.clear()
        return []
