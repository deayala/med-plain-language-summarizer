from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List
import sys

import joblib


class BinaryPLSClassifier:
    """Wrapper around the TF-IDF + Logistic Regression pipeline."""

    def __init__(self, model_path: Path, meta_path: Path | None = None):
        self.model_path = model_path
        self.meta_path = meta_path or model_path.with_name("meta.json")
        self.pipeline = self._load_pipeline()
        self.threshold = self._load_threshold()

    def _load_pipeline(self):
        if not self.model_path.exists():
            raise FileNotFoundError(f"Classifier artifact not found at {self.model_path}")
        module_main = sys.modules.get("__main__")
        if module_main is not None and not hasattr(module_main, "identity"):
            setattr(module_main, "identity", lambda x: x)
        return joblib.load(self.model_path)

    def _load_threshold(self) -> float:
        if self.meta_path.exists():
            with open(self.meta_path, "r", encoding="utf-8") as fh:
                meta = json.load(fh)
            for key in ("val_best_thr", "threshold"):
                if key in meta:
                    return float(meta[key])
        return 0.5

    def predict(self, texts: Iterable[str]) -> List[dict[str, float | str]]:
        payload = list(texts)
        if not payload:
            return []
        probs = self.pipeline.predict_proba(payload)[:, 1]
        outputs = []
        for text, prob in zip(payload, probs, strict=False):
            label = "pls" if prob >= self.threshold else "non_pls"
            outputs.append(
                {
                    "text": text,
                    "label": label,
                    "score": float(prob),
                    "threshold": self.threshold,
                }
            )
        return outputs
