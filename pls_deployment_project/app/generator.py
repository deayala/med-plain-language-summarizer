from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

import requests

from app.config import GenerationDefaults, Settings
from app.schemas import ReadabilityMetrics
from src.readability import readability_for_summary

SYS_PROMPT = (
    "*[SYSTEM INSTRUCTION]*"
    "You are a Health Literacy Expert. Your expertise is in rewriting complex, technical medical texts into clear, simple, and accurate language for a general audience, following established health communication guidelines. "
    "*[PRIMARY GOAL]*"
    "Your main purpose is to rewrite the provided medical text into a Plain Language Summary (PLS). This summary must be easy to understand for someone with an 8th-grade reading comprehension level typical of a general middle-school student, consistent with plain-language standards used by CDC and NIH, meaning it should use simple vocabulary, short sentences, and concepts that can be understood by someone with basic middle-school literacy, while remaining completely faithful to the source's essential information, for intance, conclusions. "
)

USER_PROMPT = (
    "*[TASK INSTRUCTION]* "
    "Rewrite the following technical medical text into a Plain Language Summary (PLS). The output *MUST BE ONLY* the plain language summary without special symbols and stop tokens. "
    "*--- STRICT OUTPUT RULES ---* "
    "*1.  *ACCURACY AND COMPLETENESS:* "
    "*   The summary MUST retain all key findings, main outcomes, important safety information, conclusions, and any significant numerical results from the original text. "
    "*   Do NOT add any information, opinions, or recommendations that are not present in the source document. The summary must be based ONLY on the provided text. "
    "*2.  *CLARITY AND READABILITY:* "
    "*   Write the summary at an *8th-grade reading comprehension level typical of a general middle-school student*. "
    "*   Use short, clear, and natural-sounding sentences. "
    "*   Use the active voice whenever possible (e.g., \"Scientists tested the drug\" instead of \"The drug was tested by scientists\"). "
    "*   Avoid long, complex words when a simpler alternative exists. "
    "*3.  *TERMINOLOGY (JARGON):* "
    "*   Avoid medical jargon. "
    "*   If a technical term is absolutely essential and cannot be replaced, you MUST explain it simply in parentheses the first time it appears. (Example: \"The trial used immunotherapy (a treatment that helps the body's immune system fight cancer).\") "
    "*4.  *FORMATTING AND LANGUAGE:* "
    "⁠*   The output *MUST BE ONLY* the plain language summary without special symbols and stop tokens, *only the summary*."
    "*   The output must be written *ONLY in English*. "
    "⁠*   Structure the summary as a set of concise paragraphs. Use as many sentences as needed to include all essential information, up to a maximum length of about 500 words, however, *make sure ALL sentences are complete, which means ALL ideas are finished.*"
    "*   Do NOT include headings, bullet points, lists, citations, or URLs. "
    "*--- SOURCE TECHNICAL TEXT ---* "
    "\n⁠<document>"
	"⁠{technical_text}"
	"⁠</document>"
)


@dataclass
class Candidate:
    text: str
    score: float
    metrics: ReadabilityMetrics


class HFInferenceClient:
    def __init__(self, url: str, token: str | None, timeout: int):
        if not url:
            raise ValueError("HF endpoint URL is required for remote inference")
        if not token:
            raise ValueError("HF token is required for remote inference")
        self.url = url
        self.token = token
        self.timeout = timeout

    def generate(self, prompt: str, overrides: GenerationDefaults) -> str:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": overrides.max_new_tokens,
                "min_new_tokens": overrides.min_new_tokens,
                "temperature": overrides.temperature,
                "top_p": overrides.top_p,
                "no_repeat_ngram_size": overrides.no_repeat_ngram_size,
                "repetition_penalty": overrides.repetition_penalty,
                "return_full_text": False,
            },
        }
        resp = requests.post(self.url, headers=headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data and "generated_text" in data[0]:
            return str(data[0]["generated_text"])
        if isinstance(data, dict) and "generated_text" in data:
            return str(data["generated_text"])
        if isinstance(data, str):
            return data
        return str(data)


class OpenAIChatClient:
    """Minimal OpenAI-compatible client (used by vLLM /chat/completions endpoints)."""

    def __init__(self, url: str, token: str | None, model_name: str, timeout: int):
        if not url:
            raise ValueError("Chat endpoint URL is required")
        if not model_name:
            raise ValueError("hf_chat_model_name must be configured")
        self.url = url
        self.token = token
        self.model_name = model_name
        self.timeout = timeout

    def generate(self, system_prompt: str, article: str, overrides: GenerationDefaults) -> str:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": article},
            ],
            "max_tokens": overrides.max_new_tokens,
            "temperature": overrides.temperature,
            "top_p": overrides.top_p,
            "n": 1,
        }
        resp = requests.post(self.url, headers=headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        return self._extract_text(data)

    def _extract_text(self, payload: Any) -> str:
        if isinstance(payload, dict):
            choices = payload.get("choices")
            if isinstance(choices, list):
                for choice in choices:
                    text = self._choice_text(choice)
                    if text:
                        return text
        raise ValueError("Unexpected payload from OpenAI-compatible endpoint")

    def _choice_text(self, choice: Any) -> str | None:
        if not isinstance(choice, dict):
            return None
        message = choice.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts: list[str] = []
                for part in content:
                    if isinstance(part, dict):
                        text = part.get("text")
                        if isinstance(text, str):
                            parts.append(text)
                if parts:
                    return "".join(parts)
        text = choice.get("text")
        if isinstance(text, str):
            return text
        return None


class DummyGenerator:
    """Fallback to keep CI fast when artifacts are missing."""

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    def __call__(self, article: str, *_args, **_kwargs) -> str:
        clean = re.sub(r"\s+", " ", article.strip())
        snippet = clean[:180]
        return (
            "Plain summary preview: "
            + snippet
            + ("..." if len(clean) > len(snippet) else "")
        )


class PLSGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.generator_name = "dry-run"
        self._remote_client: HFInferenceClient | None = None
        self._chat_client: OpenAIChatClient | None = None
        self._driver: Callable[[str], str] = DummyGenerator(SYS_PROMPT)
        if settings.dry_run:
            return
        if not settings.hf_endpoint_url:
            raise RuntimeError("HF_ENDPOINT_URL must be configured when DRY_RUN=0")
        if self._is_chat_endpoint(settings.hf_endpoint_url):
            self._chat_client = OpenAIChatClient(
                url=settings.hf_endpoint_url,
                token=settings.hf_token,
                model_name=settings.hf_chat_model_name,
                timeout=settings.hf_request_timeout,
            )
        else:
            self._remote_client = HFInferenceClient(
                url=settings.hf_endpoint_url,
                token=settings.hf_token,
                timeout=settings.hf_request_timeout,
            )
        self.generator_name = "hf-endpoint"

    # ---------------- Public API ----------------
    def generate(self, article: str, overrides: GenerationDefaults, best_of: int = 1) -> Candidate:
        return self._generate_best(article, overrides, best_of)

    # ---------------- Internal helpers ----------------
    def _generate_best(self, article: str, overrides: GenerationDefaults, best_of: int) -> Candidate:
        candidates = [self._generate_once(article, overrides) for _ in range(best_of)]
        return max(candidates, key=lambda cand: cand.score)

    def _generate_once(self, article: str, overrides: GenerationDefaults) -> Candidate:
        if self.generator_name == "dry-run":
            text = self._driver(article)
        elif self._chat_client is not None:
            text = self._generate_chat(article, overrides)
        elif self._remote_client is not None:
            text = self._generate_remote(article, overrides)
        else:
            text = self._driver(article)
        metrics = ReadabilityMetrics(**readability_for_summary(article, text))
        return Candidate(text=text, score=self._margin(metrics), metrics=metrics)

    def _generate_remote(self, article: str, overrides: GenerationDefaults) -> str:
        if self._remote_client is None:
            raise RuntimeError("Remote inference requested but client not initialized")
        prompt = self._build_prompt(article)
        return self._clean_text(self._remote_client.generate(prompt, overrides))

    def _generate_chat(self, article: str, overrides: GenerationDefaults) -> str:
        if self._chat_client is None:
            raise RuntimeError("Chat inference requested but client not initialized")
        return self._clean_text(self._chat_client.generate(SYS_PROMPT, article, overrides))

    @staticmethod
    def _build_prompt(article: str) -> str:
        segments = [
            "<|im_start|>system",
            SYS_PROMPT,
            "<|im_end|>",
            "<|im_start|>user",
            USER_PROMPT.format(technical_text=article),
            "<|im_end|>",
            "<|im_start|>assistant",
        ]
        return "\n".join(segments)

    @staticmethod
    def _clean_text(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _margin(self, metrics: ReadabilityMetrics) -> float:
        target = {
            "flesch_reading_ease": ("min", 60.0),
            "flesch_kincaid_grade": ("max", 6.0),
            "gunning_fog": ("max", 8.0),
            "dale_chall_score": ("max", 8.0),
        }
        score = 0.0
        for attr, (mode, thr) in target.items():
            value = getattr(metrics, attr)
            if value is None:
                continue
            margin = value - thr if mode == "min" else thr - value
            score += margin
        return score

    @staticmethod
    def _is_chat_endpoint(url: str) -> bool:
        normalized = url.lower()
        return "/chat/completions" in normalized or "/v1/completions" in normalized


if __name__ == "__main__":  # pragma: no cover
    from app.config import get_settings

    cfg = get_settings()
    gen = PLSGenerator(cfg)
    sample = (
        "Background: Dementia affects memory and thinking. \n"
        "Objective: compare stopping vs continuing cholinesterase inhibitors."
    )
    candidate = gen.generate(sample, cfg.generation, best_of=1)
    print("Generator:", gen.generator_name)
    print(candidate.text)
