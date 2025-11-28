from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AlignScoreRequest(BaseModel):
    technical_text: str = Field(..., min_length=30, description="Original technical snippet")
    generation: str = Field(..., min_length=30, description="Candidate summary to compare")

    @field_validator("technical_text", "generation")
    @classmethod
    def _normalize(cls, value: str) -> str:  # type: ignore[override]
        cleaned = " ".join(value.split())
        if len(cleaned) < 30:
            raise ValueError("Inputs must contain at least 30 characters")
        return cleaned


class AlignScoreResponse(BaseModel):
    align_score: float
    model_name: str
    device: Literal["cpu", "cuda"]
    batch_size: int


class HealthResponse(BaseModel):
    status: Literal["ok"]
    detail: str
    config: dict[str, str | int | None]
