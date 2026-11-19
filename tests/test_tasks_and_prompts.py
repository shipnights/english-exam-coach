import random

import pytest

from english_exam_coach.prompts import PROMPTS, get_prompt, prompts_for, random_prompt
from english_exam_coach.tasks import TASKS, Scale, find_task, tasks_by_track


def test_task_ids_are_unique_and_findable():
    ids = [task.id for task in TASKS]
    assert len(ids) == len(set(ids))
    assert all(find_task(i) is not None for i in ids)
    assert find_task("nope") is None


@pytest.mark.parametrize("task", TASKS, ids=lambda t: t.id)
def test_every_task_is_well_formed(task):
    assert task.minutes > 0
    assert task.min_words > 0
    assert task.max_words is None or task.max_words >= task.min_words
    assert len(task.criteria) == 4 and len(set(task.criteria)) == 4
    assert task.scale.minimum < task.scale.maximum
    assert task.target_text


@pytest.mark.parametrize("task", TASKS, ids=lambda t: t.id)
def test_every_task_has_prompts(task):
    assert len(prompts_for(task.id)) >= 3


def test_prompt_ids_are_unique_and_belong_to_a_task():
    ids = [p.id for p in PROMPTS]
    assert len(ids) == len(set(ids))
    assert all(find_task(p.task_id) for p in PROMPTS)
    assert get_prompt("missing") is None


def test_data_prompts_have_a_header_and_rectangular_rows():
    for prompt in prompts_for("ielts-w1"):
        assert prompt.table is not None
        widths = {len(row) for row in prompt.table}
        assert len(widths) == 1 and len(prompt.table) >= 3


def test_random_prompt_is_seedable_and_task_scoped():
    first = random_prompt("celpip-w2", random.Random(1))
    again = random_prompt("celpip-w2", random.Random(1))
    assert first == again and first.task_id == "celpip-w2"
    assert random_prompt("unknown") is None


def test_tasks_group_by_track_label():
    groups = tasks_by_track()
    assert list(groups) == ["IELTS-style", "CELPIP-style"]
    assert [t.id for t in groups["CELPIP-style"]] == ["celpip-w1", "celpip-w2"]


def test_scale_snaps_to_steps_and_clamps():
    bands = Scale(0, 9, 0.5, "band")
    assert bands.snap(6.26) == 6.5
    assert bands.snap(6.24) == 6.0
    assert bands.snap(-3) == 0
    assert bands.snap(12) == 9
    levels = Scale(1, 12, 1, "level")
    assert levels.snap(7.5) == 8
    assert levels.snap(0) == 1
