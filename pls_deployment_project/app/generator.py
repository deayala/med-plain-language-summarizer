from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

import requests

from app.config import GenerationDefaults, Settings
from app.schemas import ReadabilityMetrics
from src.readability import readability_for_summary

SYS_PROMPT = (
    "You are a biomedical plain-language specialist. Rewrite the source text as one "
    "paragraph, 4-6 sentences (12-16 words), active voice, third person. Use clear "
    "English, explain unavoidable jargon once in parentheses, keep every verified fact, "
    "and never invent data, opinions, or recommendations."
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
        self._driver: Callable[[str], str] = DummyGenerator(SYS_PROMPT)
        if settings.dry_run:
            return
        if not settings.hf_endpoint_url:
            raise RuntimeError("HF_ENDPOINT_URL must be configured when DRY_RUN=0")
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
        if self.generator_name == "dry-run" or self._remote_client is None:
            text = self._driver(article)
        else:
            text = self._generate_remote(article, overrides)
        metrics = ReadabilityMetrics(**readability_for_summary(article, text))
        return Candidate(text=text, score=self._margin(metrics), metrics=metrics)

    def _generate_remote(self, article: str, overrides: GenerationDefaults) -> str:
        if self._remote_client is None:
            raise RuntimeError("Remote inference requested but client not initialized")
        prompt = self._build_prompt(article)
        return self._clean_text(self._remote_client.generate(prompt, overrides))

    @staticmethod
    def _build_prompt(article: str) -> str:
        segments = [
            "<|im_start|>system",
            SYS_PROMPT,
            "<|im_end|>",
            "<|im_start|>user",
            article,
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
