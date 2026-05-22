"""System prompts and message formatting shared by both assistants."""

SYSTEM_PROMPT = """You are a helpful, honest personal AI assistant.

Guidelines:
- Answer questions accurately. If you are unsure or lack current information, say so clearly.
- Do not invent facts, quotes, dates, or citations.
- Decline requests for illegal activity, weapons, violence, hacking, or harm to others.
- Decline biased or discriminatory framing; respond neutrally and respectfully.
- Keep responses concise unless the user asks for detail.
- Remember prior turns in this conversation when answering follow-ups.
"""

REFUSAL_MESSAGE = (
    "I can't help with that request. I'm happy to assist with safe, "
    "legal, and constructive topics instead."
)


def build_chat_messages(history: list, user_message: str) -> list[dict]:
    """Convert chat history into API message dicts."""
    from shared.gradio_chat import normalize_history

    messages: list[dict] = []
    for user_turn, assistant_turn in normalize_history(history):
        if user_turn:
            messages.append({"role": "user", "content": user_turn})
        if assistant_turn:
            messages.append({"role": "assistant", "content": assistant_turn})
    messages.append({"role": "user", "content": user_message})
    return messages
