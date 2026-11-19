"""Measurable facts about a piece of writing. No AI involved, fully deterministic."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass

_WORD_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_PARAGRAPH_SPLIT = re.compile(r"\n\s*\n")

# Long common words that would otherwise dominate the "repeated words" list.
_COMMON_LONG_WORDS = frozenset(
    {"about", "after", "again", "because", "before", "being", "could", "every", "other",
     "their", "there", "these", "those", "which", "while", "would", "should", "where"}
)


def words_in(text: str) -> list[str]:
    """Return the words in `text`, lower-cased."""
    return [match.group(0).lower() for match in _WORD_RE.finditer(text)]


@dataclass(frozen=True)
class Metrics:
    words: int
    unique_words: int
    sentences: int
    paragraphs: int
    avg_sentence_words: float
    longest_sentence_words: int
    type_token_ratio: float
    repeated_words: tuple[tuple[str, int], ...]

    def to_dict(self) -> dict:
        return asdict(self)


def analyze(text: str) -> Metrics:
    """Measure `text`."""
    text = text.strip()
    words = words_in(text)
    sentences = [s for s in _SENTENCE_SPLIT.split(text) if words_in(s)]
    paragraphs = [p for p in _PARAGRAPH_SPLIT.split(text) if words_in(p)]
    sentence_lengths = [len(words_in(s)) for s in sentences]

    counts = Counter(w for w in words if len(w) >= 5 and w not in _COMMON_LONG_WORDS)
    repeated = tuple(
        sorted(((w, n) for w, n in counts.items() if n >= 3), key=lambda item: (-item[1], item[0]))[:5]
    )
    unique = len(set(words))
    return Metrics(
        words=len(words),
        unique_words=unique,
        sentences=len(sentences),
        paragraphs=len(paragraphs),
        avg_sentence_words=round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0.0,
        longest_sentence_words=max(sentence_lengths, default=0),
        type_token_ratio=round(unique / len(words), 3) if words else 0.0,
        repeated_words=repeated,
    )


def target_status(words: int, min_words: int, max_words: int | None) -> str:
    """Return "under", "ok" or "over" for a word count against a target range."""
    if words < min_words:
        return "under"
    if max_words is not None and words > max_words:
        return "over"
    return "ok"
