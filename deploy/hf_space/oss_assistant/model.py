"""OSS model backend: local transformers or Hugging Face Inference API."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from shared.prompts import SYSTEM_PROMPT

load_dotenv()

DEFAULT_MODEL_ID = os.getenv("OSS_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")


def _running_on_hf_space() -> bool:
    """True when app runs inside a Hugging Face Space container."""
    return bool(os.getenv("SPACE_ID") or os.getenv("SPACE_REPO_NAME"))


def _use_hf_inference_api() -> bool:
    """Serverless HF API — disabled on Spaces (use on-Space transformers instead)."""
    if _running_on_hf_space():
        return False
    return os.getenv("USE_HF_INFERENCE_API", "false").lower() in ("1", "true", "yes")


class OSSModel:
    def __init__(self, model_id: str | None = None):
        self.model_id = model_id or DEFAULT_MODEL_ID
        self._pipe = None
        self._tokenizer = None
        self._hf_client = None

    def _load_local(self) -> None:
        if self._pipe is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        use_cuda = torch.cuda.is_available()
        dtype = torch.float16 if use_cuda else torch.float32

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        load_kwargs: dict = {"torch_dtype": dtype}
        if use_cuda:
            load_kwargs["device_map"] = "auto"

        model = AutoModelForCausalLM.from_pretrained(self.model_id, **load_kwargs)
        self._pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=self._tokenizer,
            device=0 if use_cuda else -1,
        )

    def _load_hf_api(self) -> None:
        if self._hf_client is not None:
            return
        from huggingface_hub import InferenceClient

        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
        provider = os.getenv("HF_INFERENCE_PROVIDER")  # e.g. hf-inference, together, groq

        client_kwargs: dict = {"token": token}
        if provider:
            client_kwargs["provider"] = provider

        self._hf_client = InferenceClient(**client_kwargs)

    def _format_prompt(self, messages: list[dict[str, str]]) -> str:
        """Chat template for Qwen-style models (local only)."""
        if self._tokenizer is None:
            from transformers import AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)

        chat = [{"role": "system", "content": SYSTEM_PROMPT}]
        chat.extend(messages)
        return self._tokenizer.apply_chat_template(
            chat,
            tokenize=False,
            add_generation_prompt=True,
        )

    def generate(self, messages: list[dict[str, str]], max_new_tokens: int = 512) -> str:
        if _use_hf_inference_api():
            try:
                return self._generate_hf_api(messages, max_new_tokens)
            except RuntimeError as exc:
                if _should_fallback_local(str(exc)):
                    return self._generate_local(messages, max_new_tokens)
                raise
        return self._generate_local(messages, max_new_tokens)

    def _generate_local(self, messages: list[dict[str, str]], max_new_tokens: int) -> str:
        self._load_local()
        prompt = self._format_prompt(messages)
        outputs = self._pipe(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            return_full_text=False,
        )
        text = outputs[0]["generated_text"]
        return text.strip()

    def _generate_hf_api(self, messages: list[dict[str, str]], max_new_tokens: int) -> str:
        """Use HF chat/completions API only (conversational). Never text-generation."""
        self._load_hf_api()
        chat = [{"role": "system", "content": SYSTEM_PROMPT}, *messages]

        errors: list[str] = []
        for name, fn in (
            ("chat.completions.create", self._hf_chat_completions),
            ("chat_completion", self._hf_chat_completion),
        ):
            try:
                return fn(chat, max_new_tokens)
            except Exception as exc:
                errors.append(f"{name}: {exc}")

        hint = (
            "Set USE_HF_INFERENCE_API=false to run locally, or set "
            "HF_INFERENCE_PROVIDER=hf-inference (or another provider that supports this model). "
            "See https://hf.co/settings/inference-providers"
        )
        raise RuntimeError(
            f"Hugging Face chat API failed for {self.model_id}. {hint} Details: {' | '.join(errors)}"
        )

    def _hf_chat_completions(self, chat: list[dict], max_new_tokens: int) -> str:
        response = self._hf_client.chat.completions.create(
            model=self.model_id,
            messages=chat,
            max_tokens=max_new_tokens,
            temperature=0.7,
        )
        return self._extract_chat_response(response)

    def _hf_chat_completion(self, chat: list[dict], max_new_tokens: int) -> str:
        response = self._hf_client.chat_completion(
            model=self.model_id,
            messages=chat,
            max_tokens=max_new_tokens,
            temperature=0.7,
        )
        return self._extract_chat_response(response)

    @staticmethod
    def _extract_chat_response(response) -> str:
        if isinstance(response, dict):
            choices = response.get("choices", [])
            if choices:
                msg = choices[0].get("message", {})
                return str(msg.get("content", "")).strip()
        if hasattr(response, "choices") and response.choices:
            choice = response.choices[0]
            if hasattr(choice, "message"):
                return str(choice.message.content or "").strip()
            if hasattr(choice, "text"):
                return str(choice.text or "").strip()
        return str(response).strip()


def _should_fallback_local(error_text: str) -> bool:
    """HF serverless API often does not host small models like Qwen2.5-0.5B."""
    markers = (
        "model_not_supported",
        "not supported by any provider",
        "model is not supported",
    )
    return any(m in error_text.lower() for m in markers)


_model_instance: OSSModel | None = None


def get_model() -> OSSModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = OSSModel()
    return _model_instance
