"""Aggregate evaluation metrics from results CSV."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / "data" / "eval_results" / "eval_results.csv"


def load_results(path: Path | None = None) -> pd.DataFrame:
    path = path or RESULTS_PATH
    if not path.exists():
        raise FileNotFoundError(f"No results at {path}. Run evaluation/runner.py first.")
    return pd.read_csv(path)


def compute_metrics(df: pd.DataFrame) -> dict:
    metrics: dict = {}

    for assistant in df["assistant"].unique():
        sub = df[df["assistant"] == assistant]
        m: dict = {
            "avg_latency_ms": sub["latency_ms"].mean(),
            "n_prompts": len(sub),
        }

        if "judge_hallucinated" in sub.columns:
            trap = sub[sub["category"].isin(["hallucination_trap", "factual"])]
            if len(trap):
                hall_col = trap["judge_hallucinated"].astype(str).str.lower() == "true"
                m["hallucination_rate_pct"] = round(100 * hall_col.mean(), 1)

            harmful = sub[sub["category"].isin(["jailbreak", "harmful"])]
            if len(harmful) and "judge_refused_harmful" in harmful.columns:
                refused = harmful["judge_refused_harmful"].astype(str).str.lower() == "true"
                m["safety_refusal_rate_pct"] = round(100 * refused.mean(), 1)

            bias = sub[sub["category"] == "bias"]
            if len(bias) and "judge_bias_handling" in bias.columns:
                m["avg_bias_score"] = bias["judge_bias_handling"].astype(float).mean()

            for col in [
                "judge_accuracy",
                "judge_harmlessness",
                "judge_hallucination",
                "judge_refusal_quality",
            ]:
                if col in sub.columns:
                    m[col.replace("judge_", "avg_")] = (
                        sub[col].astype(float, errors="ignore").mean()
                    )

        metrics[assistant] = m

    return metrics


def metrics_table(df: pd.DataFrame) -> pd.DataFrame:
    m = compute_metrics(df)
    return pd.DataFrame(m).T
