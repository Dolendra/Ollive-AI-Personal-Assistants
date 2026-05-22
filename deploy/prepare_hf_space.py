"""Copy assistant code into deploy folders for Hugging Face Spaces upload."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = Path(__file__).parent

BUNDLES = {
    "hf_space": ["oss_assistant", "shared"],
    "hf_space_frontier": ["frontier_assistant", "shared"],
}


def copy_bundle(space_dir: Path, folders: list[str]) -> None:
    for folder in folders:
        src = ROOT / folder
        dest = space_dir / folder
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        print(f"  {folder} -> {dest}")


def main():
    for space_name, folders in BUNDLES.items():
        target = DEPLOY / space_name
        print(f"\n{space_name}/")
        copy_bundle(target, folders)
    print("\nReady to deploy:")
    print("  OSS:       upload deploy/hf_space/  -> huggingface.co/spaces/<you>/ollive-oss-assistant")
    print("  Frontier:  upload deploy/hf_space_frontier/ -> add GROQ_API_KEY secret")
    print("\nSee docs/DEPLOY.md for step-by-step instructions.")


if __name__ == "__main__":
    main()
