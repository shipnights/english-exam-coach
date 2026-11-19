"""Task formats the coach can practise.

The numbers below (minutes, word targets, score scales) describe the publicly
published shape of each task and can change. Check the official test
information before relying on them. Everything here is written in my own words;
no official test material is included.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Scale:
    """A score scale, such as bands 0-9 in half steps or levels 1-12."""

    minimum: float
    maximum: float
    step: float
    label: str

    def snap(self, value: float) -> float:
        """Clamp `value` into the scale and round it to the nearest step."""
        clamped = min(max(value, self.minimum), self.maximum)
        snapped = math.floor(clamped / self.step + 0.5) * self.step
        return min(max(snapped, self.minimum), self.maximum)


@dataclass(frozen=True)
class Task:
    id: str
    track: str
    track_label: str
    name: str
    minutes: int
    min_words: int
    max_words: int | None
    instructions: str
    criteria: tuple[str, ...]
    scale: Scale

    @property
    def target_text(self) -> str:
        if self.max_words:
            return f"{self.min_words}-{self.max_words} words"
        return f"at least {self.min_words} words"


_IELTS_SCALE = Scale(minimum=0, maximum=9, step=0.5, label="band")
_CELPIP_SCALE = Scale(minimum=1, maximum=12, step=1, label="level")

_CELPIP_CRITERIA = ("Content and Coherence", "Vocabulary", "Readability", "Task Fulfillment")


def _ielts_criteria(first: str) -> tuple[str, ...]:
    return (first, "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy")


TASKS: tuple[Task, ...] = (
    Task(
        id="ielts-w1",
        track="ielts",
        track_label="IELTS-style",
        name="Describe data",
        minutes=20,
        min_words=150,
        max_words=None,
        instructions=(
            "Describe the data in the table in your own words. Pick out the main features and "
            "compare figures where it helps the reader. Do not give opinions."
        ),
        criteria=_ielts_criteria("Task Achievement"),
        scale=_IELTS_SCALE,
    ),
    Task(
        id="ielts-w2",
        track="ielts",
        track_label="IELTS-style",
        name="Essay",
        minutes=40,
        min_words=250,
        max_words=None,
        instructions=(
            "Write an essay that answers the question. Give reasons for your position and "
            "support them with relevant examples."
        ),
        criteria=_ielts_criteria("Task Response"),
        scale=_IELTS_SCALE,
    ),
    Task(
        id="celpip-w1",
        track="celpip",
        track_label="CELPIP-style",
        name="Write an email",
        minutes=27,
        min_words=150,
        max_words=200,
        instructions=(
            "Write an email for the situation described. Cover every point it asks for and use a "
            "tone that suits the person you are writing to."
        ),
        criteria=_CELPIP_CRITERIA,
        scale=_CELPIP_SCALE,
    ),
    Task(
        id="celpip-w2",
        track="celpip",
        track_label="CELPIP-style",
        name="Respond to a survey",
        minutes=26,
        min_words=150,
        max_words=200,
        instructions=(
            "Read the situation, choose one of the two options, and explain your choice with "
            "reasons and examples."
        ),
        criteria=_CELPIP_CRITERIA,
        scale=_CELPIP_SCALE,
    ),
)

_BY_ID = {task.id: task for task in TASKS}


def find_task(task_id: str) -> Task | None:
    return _BY_ID.get(task_id)


def tasks_by_track() -> dict[str, list[Task]]:
    """Group tasks by their track label, in definition order."""
    grouped: dict[str, list[Task]] = {}
    for task in TASKS:
        grouped.setdefault(task.track_label, []).append(task)
    return grouped
