"""A small bank of original practice prompts.

All prompts, and all figures in the data tables, are invented for practice. They
are not taken from any official test.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

Table = tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class Prompt:
    id: str
    task_id: str
    text: str
    table: Table | None = None


def _table(*rows: tuple[object, ...]) -> Table:
    return tuple(tuple(str(cell) for cell in row) for row in rows)


PROMPTS: tuple[Prompt, ...] = (
    # --- IELTS-style: describe data (invented figures) -------------------------------
    Prompt(
        id="ielts-w1-leisure",
        task_id="ielts-w1",
        text=(
            "The table shows the average number of hours per week that adults in four groups "
            "spent on three leisure activities in 2024."
        ),
        table=_table(
            ("Group", "Reading", "Streaming video", "Exercise"),
            ("Group A", 4.5, 9.0, 3.0),
            ("Group B", 2.0, 12.5, 2.5),
            ("Group C", 6.0, 7.0, 4.5),
            ("Group D", 3.5, 10.0, 1.5),
        ),
    ),
    Prompt(
        id="ielts-w1-cafe",
        task_id="ielts-w1",
        text="The table shows how many drinks (in thousands) a cafe chain sold in three years.",
        table=_table(
            ("Drink", "2022", "2023", "2024"),
            ("Coffee", 420, 455, 470),
            ("Tea", 180, 170, 150),
            ("Cold drinks", 90, 140, 235),
            ("Hot chocolate", 60, 62, 58),
        ),
    ),
    Prompt(
        id="ielts-w1-library",
        task_id="ielts-w1",
        text=(
            "The table shows the percentage of residents in each age group who visited a public "
            "library at least once a month in two different years."
        ),
        table=_table(
            ("Age group", "2014", "2024"),
            ("Under 18", 62, 48),
            ("18-34", 31, 36),
            ("35-54", 28, 22),
            ("55 and over", 44, 57),
        ),
    ),
    # --- IELTS-style: essay ----------------------------------------------------------
    Prompt(
        id="ielts-w2-remote",
        task_id="ielts-w2",
        text=(
            "Some people believe remote work should become the default for office jobs. Others "
            "think employees should spend most of their time in a shared workplace. Discuss both "
            "views and give your own opinion."
        ),
    ),
    Prompt(
        id="ielts-w2-transit",
        task_id="ielts-w2",
        text=(
            "Many cities are making public transport free for everyone. Do the advantages of "
            "this policy outweigh the disadvantages?"
        ),
    ),
    Prompt(
        id="ielts-w2-outdoors",
        task_id="ielts-w2",
        text=(
            "Children today spend much less time playing outdoors than earlier generations did. "
            "What are the causes of this, and what can be done about it?"
        ),
    ),
    # --- CELPIP-style: email ---------------------------------------------------------
    Prompt(
        id="celpip-w1-dog",
        task_id="celpip-w1",
        text=(
            "Your neighbour's dog barks loudly every night. Write an email to your neighbour. "
            "Describe the problem, explain how it affects you, and suggest two ways to solve it."
        ),
    ),
    Prompt(
        id="celpip-w1-laptop",
        task_id="celpip-w1",
        text=(
            "You ordered a laptop online and it arrived with a cracked screen. Write an email to "
            "the store's customer service. Explain what happened, say what you want them to do, "
            "and give a date by which you need it done."
        ),
    ),
    Prompt(
        id="celpip-w1-friend",
        task_id="celpip-w1",
        text=(
            "A friend is moving to your city next month. Write an email recommending a "
            "neighbourhood, explaining why it suits them, and offering one way you can help."
        ),
    ),
    # --- CELPIP-style: survey response -----------------------------------------------
    Prompt(
        id="celpip-w2-space",
        task_id="celpip-w2",
        text=(
            "Your city will renovate one public space. Option A: turn the old parking lot into a "
            "park. Option B: turn it into a community sports centre. Which do you choose, and why?"
        ),
    ),
    Prompt(
        id="celpip-w2-event",
        task_id="celpip-w2",
        text=(
            "Your workplace can hold one yearly event. Option A: a team trip. Option B: a "
            "donation to a local charity. Which do you prefer, and why?"
        ),
    ),
    Prompt(
        id="celpip-w2-school",
        task_id="celpip-w2",
        text=(
            "A local school can afford only one of these. Option A: new computers. Option B: a "
            "music program. Which should it choose, and why?"
        ),
    ),
)

_BY_ID = {prompt.id: prompt for prompt in PROMPTS}


def get_prompt(prompt_id: str) -> Prompt | None:
    return _BY_ID.get(prompt_id)


def prompts_for(task_id: str) -> list[Prompt]:
    return [prompt for prompt in PROMPTS if prompt.task_id == task_id]


def random_prompt(task_id: str, rng: random.Random | None = None) -> Prompt | None:
    """Pick a random prompt for a task, or None if the task has none."""
    choices = prompts_for(task_id)
    if not choices:
        return None
    return (rng or random).choice(choices)
