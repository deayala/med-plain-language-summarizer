from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class GenerationDefaults(BaseModel):
    min_new_tokens: int = Field(default=60, ge=1, le=512)
    max_new_tokens: int = Field(default=200, ge=64, le=2048)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.1, le=1.0)
    no_repeat_ngram_size: int = Field(default=3, ge=1, le=10)
    repetition_penalty: float = Field(default=1.12, ge=0.0, le=10.0)

    @field_validator("max_new_tokens")
    @classmethod
    def validate_window(cls, max_tokens: int, info):  # type: ignore[override]
        min_tokens = info.data.get("min_new_tokens", cls.model_fields["min_new_tokens"].default)
        if max_tokens <= min_tokens:
            raise ValueError("max_new_tokens must be greater than min_new_tokens")
        return max_tokens


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )

    api_title: str = "PLS Generator"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8080)

    dry_run: bool = Field(default=False)
    hf_token: str | None = Field(default=None)
    hf_endpoint_url: str | None = Field(default=None)
    hf_request_timeout: int = Field(default=60, ge=5, le=180)

    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])
    generation: GenerationDefaults = Field(default_factory=GenerationDefaults)
    classifier_model_path: Path = Field(default=Path("./models/production/tfidf_logreg/model.joblib"))
    classifier_meta_path: Path | None = None

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value):  # type: ignore[override]
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    def summary(self) -> dict[str, str | int | bool]:
        return {
            "hf_endpoint": bool(self.hf_endpoint_url),
            "dry_run": self.dry_run,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


if __name__ == "__main__":
    cfg = get_settings()
    print("Settings OK:", cfg.summary())
