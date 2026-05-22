"""Upload deploy/hf_space to your Hugging Face Space (run from project root)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parents[1]
SPACE_DIR = Path(__file__).resolve().parent / "hf_space"
DEFAULT_REPO = os.getenv("HF_SPACE_REPO", "Dolendra/ollive-oss-assistant")


def main() -> None:
    load_dotenv(ROOT / ".env")
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        print("ERROR: Set HF_TOKEN in .env (must be a Write token).")
        print("Create one: https://huggingface.co/settings/tokens")
        sys.exit(1)

    if not SPACE_DIR.is_dir():
        print("ERROR: Missing deploy/hf_space. Run: python deploy/prepare_hf_space.py")
        sys.exit(1)

    repo_id = os.getenv("HF_SPACE_REPO", DEFAULT_REPO)
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


if __name__ == "__main__":
    main()
