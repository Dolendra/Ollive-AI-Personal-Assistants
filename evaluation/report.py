"""Generate evaluation infographics and 1-page PDF report."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.metrics import compute_metrics, load_results

DOCS = ROOT / "docs"
CHARTS = DOCS / "charts"


def _safe_float(series, default=0.0):
    return pd.to_numeric(series, errors="coerce").fillna(default)


def generate_charts(df: pd.DataFrame) -> list[Path]:
    CHARTS.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    paths = []

    # Hallucination rate by assistant
    if "judge_hallucinated" in df.columns:
        trap = df[df["category"].isin(["hallucination_trap", "factual"])]
        trap = trap.copy()
        trap["hallucinated"] = trap["judge_hallucinated"].astype(str).str.lower() == "true"
        agg = trap.groupby("assistant")["hallucinated"].mean() * 100

        fig, ax = plt.subplots(figsize=(6, 4))
        agg.plot(kind="bar", ax=ax, color=["#4C78A8", "#F58518"])
        ax.set_ylabel("Hallucination rate (%)")
        ax.set_title("Hallucination Rate (factual + trap prompts)")
        ax.set_ylim(0, 100)
        plt.tight_layout()
        p = CHARTS / "hallucination_rate.png"
        fig.savefig(p, dpi=150)
        plt.close(fig)
        paths.append(p)

    # Safety refusal rate
    if "judge_refused_harmful" in df.columns:
        harmful = df[df["category"].isin(["jailbreak", "harmful"])].copy()
        harmful["refused"] = harmful["judge_refused_harmful"].astype(str).str.lower() == "true"
        agg = harmful.groupby("assistant")["refused"].mean() * 100

        fig, ax = plt.subplots(figsize=(6, 4))
        agg.plot(kind="bar", ax=ax, color=["#54A24B", "#E45756"])
        ax.set_ylabel("Appropriate refusal rate (%)")
        ax.set_title("Content Safety — Jailbreak & Harmful Prompts")
        ax.set_ylim(0, 100)
        plt.tight_layout()
        p = CHARTS / "safety_refusal.png"
        fig.savefig(p, dpi=150)
        plt.close(fig)
        paths.append(p)

    # Average judge scores
    score_cols = [
        ("judge_harmlessness", "Harmlessness"),
        ("judge_accuracy", "Accuracy"),
        ("judge_bias_handling", "Bias handling"),
    ]
    available = [(c, l) for c, l in score_cols if c in df.columns]
    if available:
        fig, ax = plt.subplots(figsize=(7, 4))
        labels = [l for _, l in available]
        x = range(len(labels))
        width = 0.35
        for i, assistant in enumerate(sorted(df["assistant"].unique())):
            sub = df[df["assistant"] == assistant]
            vals = [_safe_float(sub[c]).mean() for c, _ in available]
            offset = (i - 0.5) * width
            ax.bar([xi + offset for xi in x], vals, width, label=assistant)

        ax.set_xticks(list(x))
        ax.set_xticklabels(labels)
        ax.set_ylim(1, 5)
        ax.set_ylabel("Avg score (1-5)")
        ax.set_title("LLM-as-Judge Quality Scores")
        ax.legend()
        plt.tight_layout()
        p = CHARTS / "judge_scores.png"
        fig.savefig(p, dpi=150)
        plt.close(fig)
        paths.append(p)

    # Latency comparison
    fig, ax = plt.subplots(figsize=(6, 4))
    df.groupby("assistant")["latency_ms"].mean().plot(kind="bar", ax=ax, color=["#72B7B2", "#B279A2"])
    ax.set_ylabel("Avg latency (ms)")
    ax.set_title("Response Latency")
    plt.tight_layout()
    p = CHARTS / "latency.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    paths.append(p)

    return paths


def cost_latency_table() -> pd.DataFrame:
    """Reference cost/latency table for deployment options."""
    return pd.DataFrame(
        [
            {
                "deployment": "HF Spaces (CPU, Qwen2.5-0.5B)",
                "cost_per_1k_req_usd": "~0 (free tier)",
                "avg_latency_s": "3–15",
                "notes": "Public demo; cold start on free CPU",
            },
            {
                "deployment": "Local OSS (CPU)",
                "cost_per_1k_req_usd": "0",
                "avg_latency_s": "5–30",
                "notes": "No API cost; RAM-bound",
            },
            {
                "deployment": "Groq llama-3.3-70b-versatile",
                "cost_per_1k_req_usd": "~0 (free tier)",
                "avg_latency_s": "0.5–2",
                "notes": "Frontier assistant + eval judge; rate limits apply",
            },
        ]
    )


def generate_pdf(df: pd.DataFrame, metrics: dict, chart_paths: list[Path]) -> Path:
    DOCS.mkdir(parents=True, exist_ok=True)
    pdf_path = DOCS / "evaluation_report.pdf"

    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>AI Assistant Comparison — Evaluation Report</b>", styles["Title"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            "Comparison of <b>OSS (Qwen2.5-0.5B-Instruct)</b> vs "
            "<b>Frontier (Groq / Llama 3.3 70B)</b> on hallucination, bias, and safety.",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.15 * inch))

    # Metrics table
    table_data = [["Metric", "OSS", "Frontier"]]
    oss_m = metrics.get("oss", {})
    fr_m = metrics.get("frontier", {})

    rows = [
        ("Hallucination rate %", oss_m.get("hallucination_rate_pct"), fr_m.get("hallucination_rate_pct")),
        ("Safety refusal rate %", oss_m.get("safety_refusal_rate_pct"), fr_m.get("safety_refusal_rate_pct")),
        ("Avg harmlessness (1-5)", oss_m.get("avg_harmlessness"), fr_m.get("avg_harmlessness")),
        ("Avg accuracy (1-5)", oss_m.get("avg_accuracy"), fr_m.get("avg_accuracy")),
        ("Avg latency (ms)", round(oss_m.get("avg_latency_ms", 0), 1), round(fr_m.get("avg_latency_ms", 0), 1)),
    ]
    for label, o, f in rows:
        table_data.append([label, str(o if o is not None else "N/A"), str(f if f is not None else "N/A")])

    t = Table(table_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("<b>Recommendations</b>", styles["Heading2"]))
    story.append(
        Paragraph(
            "<b>Frontier</b> is recommended for production user-facing assistants requiring "
            "strong refusals, lower hallucination on trap prompts, and faster responses. "
            "<b>OSS</b> suits offline/private workflows, cost-sensitive prototypes, and "
            "environments where data cannot leave the device — with added guardrails and "
            "optional RAG for factual tasks.",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.15 * inch))

    # Embed charts (fit width)
    for cp in chart_paths[:3]:
        if cp.exists():
            story.append(Image(str(cp), width=6.5 * inch, height=4 * inch))
            story.append(Spacer(1, 0.1 * inch))

    doc.build(story)
    print(f"PDF saved to {pdf_path}")
    return pdf_path


def main():
    try:
        df = load_results()
    except FileNotFoundError:
        print("No eval results found. Run: python evaluation/runner.py --mock --limit 5")
        print("Or full eval with API keys: python evaluation/runner.py")
        return

    metrics = compute_metrics(df)
    charts = generate_charts(df)
    cost_latency_table().to_csv(DOCS / "cost_latency_table.csv", index=False)
    generate_pdf(df, metrics, charts)

    # Markdown summary
    md = DOCS / "evaluation_report.md"
    with open(md, "w", encoding="utf-8") as f:
        f.write("# Evaluation Report\n\n")
        f.write("## Metrics\n\n")
        f.write(pd.DataFrame(metrics).T.to_string())
        f.write("\n\n## Charts\n\n")
        for c in charts:
            f.write(f"![{c.stem}](charts/{c.name})\n\n")
    print(f"Markdown report: {md}")


if __name__ == "__main__":
    main()
