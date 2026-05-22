# Run OSS assistant on Hugging Face Space only

You do **not** need to run Qwen on your laptop. The public Space runs the model on Hugging Face hardware.

---

## Step 1 — Build the Space folder

```powershell
cd D:\ollive_AIML
python deploy\prepare_hf_space.py
```

This refreshes `deploy/hf_space/` with all code needed for the Space.

---

## Step 2 — Create / update your Space

### Option A — Web upload (fastest)

1. Open [huggingface.co/spaces/Dolendra/ollive-oss-assistant](https://huggingface.co/spaces/Dolendra/ollive-oss-assistant) (or create a new Gradio Space).
2. **Files** tab → upload **all** files from `deploy/hf_space/`:
   - `app.py`, `README.md`, `requirements.txt`
   - folders `oss_assistant/`, `shared/`
3. Wait for **Building** → **Running** (5–15 min first time).

### Option B — Python upload (what you used)

From **project root** `D:\ollive_AIML` (not inside `deploy/hf_space`):

```powershell
python deploy\prepare_hf_space.py
python deploy\upload_space.py
```

Requires `HF_TOKEN` in `.env` with **Write** permission ([create token](https://huggingface.co/settings/tokens)).

### Option C — Git push

```powershell
cd D:\ollive_AIML
.\deploy\publish_space.ps1 -SpaceUser Dolendra -SpaceName ollive-oss-assistant
```

(Run from project root — not from `deploy/hf_space`.)

---

## Step 3 — Your public demo URL

```
https://huggingface.co/spaces/Dolendra/ollive-oss-assistant
```

Share this link in README and submission email. No localhost required.

---

## Settings (Space)

| Variable | Required? |
|----------|-----------|
| `USE_HF_INFERENCE_API` | **No** — leave unset (app forces off on Space) |
| `HF_TOKEN` | No for public Qwen model |
| `OSS_MODEL_ID` | Optional; default `Qwen/Qwen2.5-0.5B-Instruct` |

---

## What runs where

```
Visitor browser  →  HF Space URL  →  Gradio UI  →  Qwen on Space CPU
```

Not your PC. Not HF serverless Inference API.

---

## Frontier assistant (second Space — Groq)

OSS is already on: `https://huggingface.co/spaces/Dolendra/ollive-oss-assistant`

### 1. Create a new Space

1. [huggingface.co/new-space](https://huggingface.co/new-space)
2. Name: **`ollive-frontier-assistant`**
3. SDK: **Gradio**
4. Owner: **Dolendra**

### 2. Upload code

```powershell
cd D:\ollive_AIML
python deploy\prepare_hf_space.py
python deploy\upload_frontier_space.py
```

### 3. Add Groq secret (required)

Space → **Settings** → **Repository secrets**:

| Name | Value |
|------|--------|
| `GROQ_API_KEY` | your key from [console.groq.com/keys](https://console.groq.com/keys) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` (optional) |

Click **Restart Space** after adding secrets.

### 4. Public URL

```
https://huggingface.co/spaces/Dolendra/ollive-frontier-assistant
```

No model download on the Space — only Groq API calls.

---

## Evaluation (runs on your PC once)

Eval scripts still run locally with Groq judge — see README § Evaluation. The **demo** for reviewers is the Space URL only.
