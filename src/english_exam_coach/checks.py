"""Plain-language checks built from measured facts. These are heuristics, not an assessment."""

from __future__ import annotations

from dataclasses import dataclass

from .metrics import Metrics, target_status
from .tasks import Task


@dataclass(frozen=True)
class Checks:
    strengths: tuple[str, ...]
    improvements: tuple[str, ...]


def measured_checks(metrics: Metrics, task: Task) -> Checks:
    """Turn `metrics` into short, honest notes about length, sentences and word variety."""
    strengths: list[str] = []
    improvements: list[str] = []

    status = target_status(metrics.words, task.min_words, task.max_words)
    if status == "ok":
        strengths.append(f"Length is on target: {metrics.words} words ({task.target_text}).")
    elif status == "under":
        improvements.append(
            f"Too short: {metrics.words} words, and the target is {task.target_text}."
        )
    else:
        improvements.append(
            f"Too long: {metrics.words} words, and the target is {task.target_text}."
        )

    if metrics.sentences:
        if metrics.avg_sentence_words > 28:
            improvements.append(
                f"Sentences average {metrics.avg_sentence_words:g} words. Split the longest ones."
            )
        elif metrics.avg_sentence_words < 9 and metrics.words >= 60:
            improvements.append(
                f"Sentences average only {metrics.avg_sentence_words:g} words. "
                "Join some to vary the rhythm."
            )
        else:
            strengths.append(f"Sentence length is balanced (average {metrics.avg_sentence_words:g} words).")

    if metrics.words >= 100:
        if metrics.type_token_ratio < 0.45:
            improvements.append(
                f"Vocabulary repeats a lot (only {metrics.type_token_ratio:.0%} of words are different). "
                "Vary your key words."
            )
        if metrics.paragraphs == 1 and metrics.words > 120:
            improvements.append("Everything is in one block. Break it into paragraphs.")

    if metrics.repeated_words:
        listed = ", ".join(f"{word} x{count}" for word, count in metrics.repeated_words)
        improvements.append(f"Repeated words: {listed}. Try synonyms or restructure.")

    return Checks(strengths=tuple(strengths), improvements=tuple(improvements))
