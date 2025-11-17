from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SummarizeRequest(BaseModel):
    article: str = Field(..., min_length=32, description="Raw medical or clinical text")
    best_of: int = Field(default=1, ge=1, le=5)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, ge=0.1, le=1.0)
    max_new_tokens: int | None = Field(default=None, ge=64, le=2048)
    min_new_tokens: int | None = Field(default=None, ge=1, le=512)
    no_repeat_ngram_size: int | None = Field(default=None, ge=1, le=10)
    repetition_penalty: float | None = Field(default=None, ge=0.0, le=10.0)

    @field_validator("article")
    @classmethod
    def strip_article(cls, val: str) -> str:  # type: ignore[override]
        clean = val.strip()
        if len(clean.split()) < 20:
            raise ValueError("Article must have at least 20 words to build a summary")
        return clean


class ReadabilityMetrics(BaseModel):
    flesch_reading_ease: float | None = None
    flesch_kincaid_grade: float | None = None
    coleman_liau_index: float | None = None
    gunning_fog: float | None = None
    smog_index: float | None = None
    dale_chall_score: float | None = None
    avg_words_per_sentence: float | None = None
    compression_ratio: float | None = None
    number_recall: float | None = None
    repetition_ratio: float | None = None
    jargon_density: float | None = None


class ReadabilityBreakdown(BaseModel):
    source: ReadabilityMetrics
    generated: ReadabilityMetrics


class SummarizeResponse(BaseModel):
    summary: str
    latency_ms: int
    generator: Literal["gpu", "cpu", "dry-run", "hf-endpoint"]
    readability: ReadabilityBreakdown
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    status: Literal["ok"]
    detail: str
    config: dict[str, str | int | bool]


class ClassificationRequest(BaseModel):
    text: str = Field(..., min_length=32, description="Text passage to classify as PLS or not")

    @field_validator("text")
    @classmethod
    def strip_text(cls, val: str) -> str:  # type: ignore[override]
        clean = val.strip()
        if len(clean.split()) < 5:
            raise ValueError("Text must contain at least five words for classification")
        return clean


class ClassifiedText(BaseModel):
    text: str
    label: Literal["pls", "non_pls"]
    score: float = Field(ge=0.0, le=1.0)
    threshold: float = Field(ge=0.0, le=1.0)


class ClassificationResponse(ClassifiedText):
    ...


class BulkClassificationRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=128)

    @field_validator("texts")
    @classmethod
    def validate_entries(cls, payload: list[str]) -> list[str]:  # type: ignore[override]
        cleaned = []
        for text in payload:
            stripped = text.strip()
            if len(stripped.split()) < 5:
                raise ValueError("Each text must include at least five words")
            cleaned.append(stripped)
        return cleaned


class BulkClassificationResponse(BaseModel):
    results: list[ClassifiedText]
