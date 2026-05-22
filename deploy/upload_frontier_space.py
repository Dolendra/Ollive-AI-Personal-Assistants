"""Upload deploy/hf_space_frontier to your Hugging Face Space (run from project root)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parents[1]
SPACE_DIR = Path(__file__).resolve().parent / "hf_space_frontier"
DEFAULT_REPO = "Dolendra/ollive-frontier-assistant"


def main() -> None:
    load_dotenv(ROOT / ".env")
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        print("ERROR: Set HF_TOKEN in .env (Write token).")
        print("https://huggingface.co/settings/tokens")
        sys.exit(1)

    if not SPACE_DIR.is_dir():
        print("ERROR: Run first: python deploy/prepare_hf_space.py")
        sys.exit(1)

    repo_id = os.getenv("HF_SPACE_FRONTIER_REPO", DEFAULT_REPO)
    print(f"Uploading {SPACE_DIR} -> spaces/{repo_id}")

    api = HfApi(token=token)
    api.upload_folder(
        folder_path=str(SPACE_DIR),
        repo_id=repo_id,
        repo_type="space",
        token=token,
    )
    print("Upload complete!")
    print(f"Demo URL: https://huggingface.co/spaces/{repo_id}")
    print()
    print("IMPORTANT: In Space Settings → Repository secrets, add:")
    print("  GROQ_API_KEY = your Groq key (https://console.groq.com/keys)")
    print("  GROQ_MODEL   = llama-3.3-70b-versatile  (optional)")


if __name__ == "__main__":
    main()
