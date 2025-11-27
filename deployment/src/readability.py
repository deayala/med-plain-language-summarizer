from __future__ import annotations

from collections import Counter
import re
from typing import Callable, Dict

try:  # pragma: no cover - optional heavy dependency
    import textstat
except Exception:  # pragma: no cover
    textstat = None

TOKEN_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+(?:\.\d+)?")
NUMBER_PATTERN = re.compile(r"\d+(?:\.\d+)?")
JARGON_HINTS = {
    "etiology",
    "pathophysiology",
    "comorbidity",
    "morbidity",
    "adverse",
    "intervention",
    "randomized",
    "placebo",
    "biomarker",
    "cohort",
    "hazard",
    "endpoint",
    "efficacy",
    "incidence",
    "prevalence",
    "contraindication",
    "pharmacokinetics",
    "titration",
}


def _safe_textstat(fn: Callable[[str], float], text: str) -> float | None:
    if textstat is None:
        return None
    try:
        return float(fn(text))
    except Exception:
        return None


def _tokenize(text: str) -> list[str]:
    return [tok.lower() for tok in TOKEN_PATTERN.findall(text)]


def _sentence_count(text: str) -> int:
    if textstat is not None:
        try:
            return max(1, int(textstat.sentence_count(text)))
        except Exception:
            pass
    sentences = re.split(r"[.!?]+", text)
    return max(1, sum(1 for sent in sentences if sent.strip()))


def _word_count(text: str) -> int:
    if textstat is not None:
        try:
            return max(1, int(textstat.lexicon_count(text, removepunct=True)))
        except Exception:
            pass
    return max(1, len(_tokenize(text)))


def _avg_words_per_sentence(text: str) -> float:
    return _word_count(text) / _sentence_count(text)


def _numbers_in(text: str) -> set[str]:
    return set(match.group(0) for match in NUMBER_PATTERN.finditer(text))


def _number_recall(source: str, summary: str) -> float:
    numbers = _numbers_in(source)
    if not numbers:
        return 1.0
    hits = sum(1 for num in numbers if num in summary)
    return hits / len(numbers)


def _repetition_ratio(text: str) -> float:
    tokens = _tokenize(text)
    if not tokens:
        return 0.0
    counts = Counter(tokens)
    return max(counts.values()) / len(tokens)


def _jargon_density(text: str) -> float:
    tokens = _tokenize(text)
    if not tokens:
        return 0.0
    long_words = sum(1 for tok in tokens if len(tok) >= 12)
    hints = sum(1 for tok in tokens if tok in JARGON_HINTS)
    return (long_words + hints) / len(tokens)


def readability_from_text(text: str) -> Dict[str, float | None]:
    metrics: Dict[str, float | None] = {
        "flesch_reading_ease": _safe_textstat(textstat.flesch_reading_ease, text)
        if textstat
        else None,
        "flesch_kincaid_grade": _safe_textstat(textstat.flesch_kincaid_grade, text)
        if textstat
        else None,
        "coleman_liau_index": _safe_textstat(textstat.coleman_liau_index, text)
        if textstat
        else None,
        "gunning_fog": _safe_textstat(textstat.gunning_fog, text)
        if textstat
        else None,
        "smog_index": _safe_textstat(textstat.smog_index, text)
        if textstat
        else None,
        "dale_chall_score": _safe_textstat(textstat.dale_chall_readability_score, text)
        if textstat
        else None,
    }
    metrics["avg_words_per_sentence"] = _avg_words_per_sentence(text)
    metrics["repetition_ratio"] = _repetition_ratio(text)
    metrics["jargon_density"] = _jargon_density(text)
    metrics["compression_ratio"] = None
    metrics["number_recall"] = None
    return metrics


def readability_for_summary(source: str, summary: str) -> Dict[str, float | None]:
    metrics = readability_from_text(summary)
    metrics["compression_ratio"] = len(summary) / max(1, len(source))
    metrics["number_recall"] = _number_recall(source, summary)
    return metrics
