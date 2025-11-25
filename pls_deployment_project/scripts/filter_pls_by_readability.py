#!/usr/bin/env python
"""
Filter PLS training pairs by readability targets.

Steps
-----
1. Load `data/raw/pls_train_pairs.csv`.
2. Drop duplicate `base_id` entries to keep a single article.
3. Compute classic readability metrics on each PLS text.
4. Score every summary against the requested readability targets.
5. Keep the 2,500 easiest patient summaries (lowest penalty) to use for fine-tuning.

The output CSV keeps the original columns plus the computed scores so
we can audit which samples were retained for fine-tuning.
"""
from __future__ import annotations

import csv
import math
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd

RAW_DATA_PATH = Path("data/raw/pls_train_pairs.csv")
EASY_WORDS_PATH = Path("data/dale_chall_easy_words.txt")
OUTPUT_PATH = Path("data/features/pls_train_pairs_readability.csv")
TARGET_SAMPLE_COUNT = 2500

TARGETS = {
    "flesch_reading_ease": ("min", 60.0),
    "flesch_kincaid_grade": ("max", 6.0),
    "gunning_fog_index": ("max", 8.0),
    "smog_index": ("max", 8.0),
    "coleman_liau_index": ("max", 8.0),
    "dale_chall_score": ("max", 8.0),
}

WORD_RE = re.compile(r"[a-zA-Z']+")
SENTENCE_RE = re.compile(r"[.!?]+")
VOWELS = set("aeiouy")
ALLOWED_NON_ASCII = set("’“”–—−°…•′″β±µ≤≥")


def load_easy_words(path: Path) -> set[str]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing Dale-Chall word list at {path}. Run the setup step first."
        )
    return {
        word.strip().lower()
        for word in path.read_text(encoding="utf-8").splitlines()
        if word.strip()
    }


def split_sentences(text: str) -> Iterable[str]:
    for sentence in SENTENCE_RE.split(text):
        sentence = sentence.strip()
        if sentence:
            yield sentence


def tokenize_words(text: str) -> Iterable[str]:
    for word in WORD_RE.findall(text):
        cleaned = word.strip("'").lower()
        if cleaned:
            yield cleaned


def count_syllables(word: str) -> int:
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    syllables = 0
    prev_is_vowel = False
    for char in word:
        is_vowel = char in VOWELS
        if is_vowel and not prev_is_vowel:
            syllables += 1
        prev_is_vowel = is_vowel
    if word.endswith("e") and syllables > 1:
        syllables -= 1
    if word.endswith("le") and len(word) > 2 and word[-3] not in VOWELS:
        syllables += 1
    return max(syllables, 1)


def readability_metrics(text: str, easy_words: set[str]) -> Dict[str, float]:
    sentences = list(split_sentences(text))
    sentence_count = max(len(sentences), 1)
    words = list(tokenize_words(text))
    word_count = max(len(words), 1)
    syllable_count = sum(count_syllables(word) for word in words)
    complex_words = sum(1 for word in words if count_syllables(word) >= 3)
    polysyllables = complex_words
    letters = sum(len(re.sub(r"[^a-z]", "", word)) for word in words)
    difficult_words = sum(1 for word in words if word not in easy_words)

    words_per_sentence = word_count / sentence_count
    syllables_per_word = syllable_count / word_count

    flesch = (
        206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
    )
    fkgl = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59
    fog = 0.4 * (words_per_sentence + 100 * (complex_words / word_count))

    if polysyllables == 0 or sentence_count == 0:
        smog = 0.0
    else:
        smog = 1.0430 * math.sqrt(polysyllables * (30 / sentence_count)) + 3.1291

    letters_per_100_words = (letters / word_count) * 100
    sentences_per_100_words = (sentence_count / word_count) * 100
    coleman_liau = (
        0.0588 * letters_per_100_words - 0.296 * sentences_per_100_words - 15.8
    )

    difficult_pct = (difficult_words / word_count) * 100
    dale_chall = 0.1579 * difficult_pct + 0.0496 * words_per_sentence
    if difficult_pct > 5:
        dale_chall += 3.6365

    return {
        "flesch_reading_ease": round(flesch, 3),
        "flesch_kincaid_grade": round(fkgl, 3),
        "gunning_fog_index": round(fog, 3),
        "smog_index": round(smog, 3),
        "coleman_liau_index": round(coleman_liau, 3),
        "dale_chall_score": round(dale_chall, 3),
    }


def readability_penalty(scores: Dict[str, float]) -> float:
    penalty = 0.0
    for key, (direction, threshold) in TARGETS.items():
        value = scores[key]
        if direction == "min":
            penalty += max(0.0, threshold - value)
        else:
            penalty += max(0.0, value - threshold)
    return round(penalty, 3)


def ensure_output_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def looks_like_english(text: str) -> bool:
    text = text.strip()
    if not text or "�" in text:
        return False
    ascii_like = sum(
        1 for ch in text if ch.isascii() or ch in ALLOWED_NON_ASCII or ch.isspace()
    )
    ratio = ascii_like / max(len(text), 1)
    alpha_chars = sum(1 for ch in text if ch.isalpha())
    return ratio >= 0.85 and alpha_chars >= 30


def iter_unique_records(
    input_path: Path, chunksize: int = 512
) -> Iterable[Dict[str, str]]:
    seen_ids: set[str] = set()
    for chunk in pd.read_csv(input_path, chunksize=chunksize):
        chunk = chunk.fillna("")
        for row in chunk.to_dict(orient="records"):
            base_id = str(row.get("base_id", "")).strip()
            if not base_id or base_id in seen_ids:
                continue
            seen_ids.add(base_id)
            yield row


def process_dataset(
    input_path: Path, output_path: Path, easy_words: set[str], chunksize: int = 512
) -> Tuple[int, int, int, int]:
    ensure_output_dir(output_path)
    total_rows = 0
    unique_articles = 0
    valid_articles = 0

    fieldnames = [
        "non_pls_path",
        "pls_path",
        "non_pls_text",
        "pls_text",
        "base_id",
        *TARGETS.keys(),
        "readability_penalty",
    ]

    scored_records: List[Dict[str, str]] = []
    for row in iter_unique_records(input_path, chunksize=chunksize):
        total_rows += 1
        unique_articles += 1
        pls_text = str(row.get("pls_text", "")).strip()
        non_pls_text = str(row.get("non_pls_text", "")).strip()
        if not looks_like_english(pls_text) or not looks_like_english(non_pls_text):
            continue
        valid_articles += 1

        scores = readability_metrics(pls_text, easy_words)
        penalty = readability_penalty(scores)
        scored_records.append(
            {
                "non_pls_path": row.get("non_pls_path", ""),
                "pls_path": row.get("pls_path", ""),
                "non_pls_text": non_pls_text,
                "pls_text": pls_text,
                "base_id": str(row.get("base_id", "")).strip(),
                **scores,
                "readability_penalty": penalty,
            }
        )

    scored_records.sort(
        key=lambda item: (item["readability_penalty"], -item["flesch_reading_ease"])
    )
    kept_records = scored_records[: min(len(scored_records), TARGET_SAMPLE_COUNT)]

    with output_path.open("w", newline="", encoding="utf-8") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept_records)

    return total_rows, unique_articles, valid_articles, len(kept_records)


def main() -> None:
    easy_words = load_easy_words(EASY_WORDS_PATH)
    total, unique, valid, kept = process_dataset(
        RAW_DATA_PATH, OUTPUT_PATH, easy_words
    )
    print(f"Processed rows: {total}")
    print(f"Unique articles: {unique}")
    print(f"Valid English articles: {valid}")
    print(f"Retained samples: {kept}")
    print(f"Output saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
