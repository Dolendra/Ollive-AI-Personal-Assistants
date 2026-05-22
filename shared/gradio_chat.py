"""Gradio Chatbot history helpers — OpenAI-style messages format."""

from __future__ import annotations

ChatHistory = list[tuple[str, str]]
GradioMessages = list[dict[str, str]]


def create_chatbot(**kwargs):
    """Create gr.Chatbot (current Gradio versions use messages format only)."""
    import gradio as gr

    return gr.Chatbot(**kwargs)


def normalize_history(history: list | None) -> ChatHistory:
    """Accept Gradio messages or legacy tuples; return (user, assistant) pairs."""
    if not history:
        return []

    first = history[0]
    if isinstance(first, dict):
        return _messages_to_tuples(history)  # type: ignore[arg-type]
    if isinstance(first, (list, tuple)) and len(first) == 2:
        return [(str(u or ""), str(a or "")) for u, a in history]
    return []


def format_for_gradio(history: ChatHistory) -> GradioMessages:
    """Return history as Gradio messages: [{role, content}, ...]."""
    messages: GradioMessages = []
    for user, assistant in history:
        if user:
            messages.append({"role": "user", "content": user})
        if assistant:
            messages.append({"role": "assistant", "content": assistant})
    return messages


def _messages_to_tuples(messages: GradioMessages) -> ChatHistory:
    pairs: ChatHistory = []
    pending_user: str | None = None

    for msg in messages:
        role = msg.get("role")
        content = str(msg.get("content") or "")
        if role == "user":
            if pending_user is not None:
                pairs.append((pending_user, ""))
            pending_user = content
        elif role == "assistant":
            pairs.append((pending_user or "", content))
            pending_user = None

    if pending_user is not None:
        pairs.append((pending_user, ""))
    return pairs
