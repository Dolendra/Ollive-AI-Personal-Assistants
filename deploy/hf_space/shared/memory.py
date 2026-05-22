"""Short-term conversational memory for multi-turn chat."""

from dataclasses import dataclass, field


@dataclass
class ConversationMemory:
    """In-session message history (short-term memory)."""

    max_turns: int = 20
    messages: list[tuple[str, str]] = field(default_factory=list)

    def add_turn(self, user: str, assistant: str) -> None:
        self.messages.append((user, assistant))
        if len(self.messages) > self.max_turns:
            self.messages = self.messages[-self.max_turns :]

    def clear(self) -> None:
        self.messages.clear()

    def as_gradio_history(self) -> list[tuple[str, str]]:
        return list(self.messages)
