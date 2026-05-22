"""
Hugging Face Space entrypoint — OSS assistant.

The model runs on Hugging Face's servers (Space hardware), NOT on your laptop.
Do not set USE_HF_INFERENCE_API=true here — that serverless API does not host Qwen 0.5B.
"""

import os
import sys
from pathlib import Path

# Force on-Space inference (transformers on Space CPU/GPU)
os.environ["USE_HF_INFERENCE_API"] = "false"
os.environ.setdefault("OSS_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")

SPACE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SPACE_ROOT))

from oss_assistant.app import build_ui

demo = build_ui()

if __name__ == "__main__":
    demo.launch()
