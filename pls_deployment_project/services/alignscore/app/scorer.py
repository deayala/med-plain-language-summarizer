from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Optional

from .config import AlignSettings


@dataclass
class AlignScoreResult:
    score: float
    model_name: str
    device: str
    batch_size: int


class AlignScoreEngine:
    """Lazy loader for the AlignScore model inside the isolated service."""

    def __init__(self, settings: AlignSettings):
        self.settings = settings
        self._lock = Lock()
        self._scorer = None
        self._device = self._resolve_device()

    def _resolve_device(self) -> str:
        if self.settings.device_preference:
            return self.settings.device_preference
        try:
            import torch

            if torch.cuda.is_available():
                return "cuda"
        except Exception:
            pass
        return "cpu"

    def _load_model(self):
        from alignscore import AlignScore  # type: ignore[import-not-found]

        ckpt_path = self._resolve_checkpoint()
        self._scorer = AlignScore(
            model=self.settings.model_name,
            batch_size=self.settings.batch_size,
            device=self._device,
            ckpt_path=ckpt_path,
        )

    def _resolve_checkpoint(self) -> Optional[str]:
        if self.settings.checkpoint_path is None:
            return None
        path = self.settings.checkpoint_path
        if not path.exists():
            raise FileNotFoundError(
                f"AlignScore checkpoint not found at {path}. "
                "Mount the checkpoint and set ALIGN_CHECKPOINT_PATH."
            )
        return str(path)

    def _ensure_model(self):
        if self._scorer is not None:
            return self._scorer
        with self._lock:
            if self._scorer is None:
                self._load_model()
        return self._scorer

    def score(self, technical_text: str, generation: str) -> AlignScoreResult:
        scorer = self._ensure_model()
        results = scorer.score(
            contexts=[technical_text],
            claims=[generation],
        )
        if not results:
            raise RuntimeError("AlignScore returned no scores")
        score_value = float(results[0])
        return AlignScoreResult(
            score=score_value,
            model_name=self.settings.model_name,
            device=self._device,
            batch_size=self.settings.batch_size,
        )
