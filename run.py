"""Unified launcher for both assistants."""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Launch AI assistants")
    parser.add_argument(
        "target",
        choices=["oss", "frontier", "eval", "report"],
        help="What to run",
    )
    parser.add_argument("--limit", type=int, default=None, help="Eval prompt limit")
    parser.add_argument("--mock", action="store_true", help="Eval without judge API")
    args = parser.parse_args()

    if args.target == "oss":
        subprocess.run([sys.executable, str(ROOT / "oss_assistant" / "app.py")], check=True)
    elif args.target == "frontier":
        subprocess.run([sys.executable, str(ROOT / "frontier_assistant" / "app.py")], check=True)
    elif args.target == "eval":
        cmd = [sys.executable, str(ROOT / "evaluation" / "runner.py")]
        if args.limit:
            cmd.extend(["--limit", str(args.limit)])
        if args.mock:
            cmd.append("--mock")
        subprocess.run(cmd, check=True)
    elif args.target == "report":
        subprocess.run([sys.executable, str(ROOT / "evaluation" / "report.py")], check=True)


if __name__ == "__main__":
    main()
