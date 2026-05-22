"""Run evaluation prompts against both assistants."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from evaluation.judge import score_response
from frontier_assistant.assistant import FrontierAssistant
from oss_assistant.assistant import OSSAssistant

PROMPTS_PATH = Path(__file__).parent / "prompts.json"
RESULTS_DIR = ROOT / "data" / "eval_results"


def load_prompts() -> list[dict]:
    with open(PROMPTS_PATH, encoding="utf-8") as f:
        return json.load(f)


def run_assistant(assistant, prompt: str, history: list | None = None) -> tuple[str, list, float]:
    history = history or []
    start = time.perf_counter()
    _, updated = assistant.chat(prompt, history)
    latency = (time.perf_counter() - start) * 1000
    reply = updated[-1][1] if updated else ""
    return reply, updated, latency


def evaluate(*, use_judge: bool = True, limit: int | None = None, mock: bool = False) -> pd.DataFrame:
    prompts = load_prompts()
    if limit:
        prompts = prompts[:limit]

    oss = OSSAssistant()
    frontier = FrontierAssistant()
    rows = []

    # Memory tests need shared history within each assistant
    memory_history_oss: list = []
    memory_history_frontier: list = []

    for item in prompts:
        pid = item["id"]
        category = item["category"]
        prompt = item["prompt"]

        print(f"[{pid}] {category}: {prompt[:60]}...")

        if category == "memory":
            o_resp, memory_history_oss, o_lat = run_assistant(oss, prompt, memory_history_oss)
            f_resp, memory_history_frontier, f_lat = run_assistant(
                frontier, prompt, memory_history_frontier
            )
        else:
            o_resp, _, o_lat = run_assistant(oss, prompt, [])
            f_resp, _, f_lat = run_assistant(frontier, prompt, [])

        for assistant_type, resp, lat in [
            ("oss", o_resp, o_lat),
            ("frontier", f_resp, f_lat),
        ]:
            scores = {}
            if use_judge and not mock:
                try:
                    scores = score_response(
                        category=category, prompt=prompt, response=resp
                    )
                    time.sleep(0.3)  # rate limit courtesy
                except Exception as exc:
                    scores = {"rationale": f"judge_error: {exc}"}

            rows.append(
                {
                    "prompt_id": pid,
                    "category": category,
                    "prompt": prompt,
                    "assistant": assistant_type,
                    "response": resp,
                    "latency_ms": round(lat, 2),
                    **{f"judge_{k}": v for k, v in scores.items()},
                }
            )

    df = pd.DataFrame(rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / "eval_results.csv"
    df.to_csv(out, index=False)
    print(f"Saved results to {out}")
    return df


def main():
    parser = argparse.ArgumentParser(description="Evaluate OSS vs Frontier assistants")
    parser.add_argument("--limit", type=int, default=None, help="Max prompts to run")
    parser.add_argument("--no-judge", action="store_true", help="Skip LLM judge (faster)")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Skip judge API calls; use for CI without keys",
    )
    args = parser.parse_args()
    evaluate(use_judge=not args.no_judge, limit=args.limit, mock=args.mock)


if __name__ == "__main__":
    main()
