"""Hugging Face Space — Frontier assistant (Groq API only)."""

import os
import sys
from pathlib import Path

SPACE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SPACE_ROOT))

import gradio as gr

from frontier_assistant.app import build_ui

demo = build_ui()

# Warn in UI if secret not configured on the Space
if not os.getenv("GROQ_API_KEY"):
    with demo:
        gr.Markdown(
            "⚠️ **Add `GROQ_API_KEY`** in Space **Settings → Repository secrets**, "
            "then restart the Space."
        )

if __name__ == "__main__":
    demo.launch()
