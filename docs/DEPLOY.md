# Deploy & share (without running on your laptop)

You do **not** need `USE_HF_INFERENCE_API=true`. That flag is for Hugging Face's *paid/serverless* API, which does **not** host `Qwen2.5-0.5B`.

For a **public demo URL**, deploy to **Hugging Face Spaces**. The model runs on **HF's servers** in the cloud — same as the assignment bonus, not on your PC.

---

## 1. OSS assistant (Qwen on Space hardware)

### Prepare files

```powershell
cd D:\ollive_AIML
python deploy\prepare_hf_space.py
```

### Create the Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. **Space name:** `ollive-oss-assistant` (or match `HF_SPACE_REPO` in `.env`)
3. **SDK:** Gradio
4. **Visibility:** Public
5. Upload **everything inside** `deploy/hf_space/`:
   - `app.py`, `README.md`, `requirements.txt`
   - folders `oss_assistant/`, `shared/`

Or connect a GitHub repo and set the Space root to `deploy/hf_space`.

### Space settings

| Setting | Value |
|--------|--------|
| `USE_HF_INFERENCE_API` | **Do not set** (defaults to false on Space) |
| Secrets | Optional `HF_TOKEN` only if you use a gated model |

### Public URL

```
https://huggingface.co/spaces/<your-username>/ollive-oss-assistant
```

First chat may take **1–2 minutes** (model load on free CPU). After that, replies are faster.

**Cost:** Free tier on HF Spaces (CPU). **Latency:** ~3–15s per reply on CPU (document in your report).

---

## 2. Frontier assistant (Groq — no heavy model on Space)

Groq runs in the cloud; the Space only hosts the Gradio UI.

```powershell
python deploy\prepare_hf_space.py
```

1. New Space: `ollive-frontier-assistant`
2. Upload `deploy/hf_space_frontier/`
3. **Settings → Repository secrets:**
   - `GROQ_API_KEY` = your Groq key
   - `GROQ_MODEL` = `llama-3.3-70b-versatile` (optional)

Public URL:

```
https://huggingface.co/spaces/<your-username>/ollive-frontier-assistant
```

---

## 3. Local `.env` vs deployment

| Environment | `USE_HF_INFERENCE_API` | Where model runs |
|-------------|------------------------|------------------|
| Your PC (dev) | `false` | Your machine (slow CPU) |
| HF Space (share) | `false` (forced in `app.py`) | **Hugging Face servers** |
| HF serverless API | `true` | ❌ Qwen 0.5B not available |

---

## 4. Submission demo links

Put both URLs in README and email to work@ollive.ai:

- OSS Space: `https://huggingface.co/spaces/Dolendra/ollive-oss-assistant`
- Frontier Space: `https://huggingface.co/spaces/Dolendra/ollive-frontier-assistant`

---

## 5. Optional: temporary Gradio tunnel (not for submission)

Runs on **your** PC but gives a 72h public link:

```python
demo.launch(share=True)  # in app.py
```

Not recommended for the assignment — use HF Spaces for a stable demo.
