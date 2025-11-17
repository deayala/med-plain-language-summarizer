from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AlignSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ALIGN_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    api_title: str = "AlignScore Service"
    api_version: str = "1.0.0"
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8090)

    model_name: str = Field(default="roberta-base")
    checkpoint_path: Path | None = Field(default=None)
    batch_size: int = Field(default=4, ge=1, le=32)
    device_preference: str | None = Field(
        default=None,
        description="Force device (cpu/cuda); defaults to auto detection",
    )

    min_chars: int = Field(default=30, ge=16, le=256)

    @field_validator("device_preference")
    @classmethod
    def _normalize_device(cls, value: str | None) -> str | None:  # type: ignore[override]
        if value is None:
            return None
        lowered = value.strip().lower()
        if lowered not in {"cpu", "cuda", "auto"}:
            raise ValueError("device_preference must be cpu, cuda, or auto")
        return None if lowered == "auto" else lowered

    def summary(self) -> dict[str, str | int | None]:
        checkpoint = str(self.checkpoint_path) if self.checkpoint_path else None
        return {
            "model": self.model_name,
            "checkpoint": checkpoint,
            "batch_size": self.batch_size,
        }


@lru_cache(maxsize=1)
def get_settings() -> AlignSettings:
    return AlignSettings()


if __name__ == "__main__":  # pragma: no cover
    cfg = get_settings()
    print(cfg.summary())
