# Submission package

## Email to work@ollive.ai

**Subject:** Ollive AIML — AI Assistant Comparison Submission

**Body template:**

```
Hi Ollive team,

Please find my submission:

GitHub: <your-repo-url>
Evaluation PDF: docs/evaluation_report.pdf (attached)
Demo (optional): <HF Space URL or localhost screenshots>

Stack:
- OSS: Qwen2.5-0.5B-Instruct (Gradio + HF Spaces ready)
- Frontier: Groq llama-3.3-70b-versatile (free tier)
- Eval: 33 prompts, LLM-as-judge, infographics + PDF

Thanks,
<Your Name>
```

## Before sending

1. `git init` && push to public GitHub
2. `python evaluation/generate_sample_results.py` OR full `python evaluation/runner.py`
3. `python evaluation/report.py` → attach `docs/evaluation_report.pdf`
4. Deploy HF Space and add URL to README
