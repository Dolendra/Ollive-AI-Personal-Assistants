"""Lightweight input/output safety guardrails."""

from __future__ import annotations

import re
from dataclasses import dataclass

from shared.prompts import REFUSAL_MESSAGE

# Obvious harmful / jailbreak patterns (lightweight pre-filter)
BLOCKED_INPUT_PATTERNS = [
    r"\bignore\s+(all\s+)?(previous\s+)?instructions\b",
    r"\bjailbreak\b",
    r"\bDAN\s+mode\b",
    r"\bhow\s+to\s+(make|build|create)\s+(a\s+)?(bomb|weapon|explosive)\b",
    r"\bhow\s+to\s+(hack|ddos|phish)\b",
    r"\bkill\s+(yourself|myself|someone)\b",
]

BIAS_PROBE_PATTERNS = [
    r"\bwomen\s+.*worse\s+.*math\b",
    r"\brace\s+.*inferior\b",
    r"\bwhich\s+group\s+is\s+smarter\b",
]

COMPILED_BLOCKED = [re.compile(p, re.IGNORECASE) for p in BLOCKED_INPUT_PATTERNS]
COMPILED_BIAS = [re.compile(p, re.IGNORECASE) for p in BIAS_PROBE_PATTERNS]


@dataclass
class GuardrailResult:
    blocked: bool
    reason: str | None = None
    category: str | None = None  # jailbreak | harmful | bias_probe


def check_input(user_message: str) -> GuardrailResult:
    text = (user_message or "").strip()
    if not text:
        return GuardrailResult(blocked=True, reason="Empty message.", category="empty")

    for pattern in COMPILED_BLOCKED:
        if pattern.search(text):
            return GuardrailResult(
                blocked=True,
                reason=REFUSAL_MESSAGE,
                category="harmful_or_jailbreak",
            )

    # Bias probes are not blocked — we want the model to respond safely
    for pattern in COMPILED_BIAS:
        if pattern.search(text):
            return GuardrailResult(blocked=False, category="bias_probe")

    return GuardrailResult(blocked=False)


def sanitize_output(text: str) -> str:
    """Post-filter: trim and cap length."""
    if not text:
        return "I don't have a response for that."
    return text.strip()[:8000]
