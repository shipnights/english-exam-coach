from english_exam_coach.feedback import Feedback
from english_exam_coach.store import Store


def add(store, task_id="celpip-w1", words=120, feedback=None, error=""):
    return store.add_attempt(
        task_id=task_id, prompt_id="p", prompt_text="Prompt", response_text="Some words here",
        seconds_used=75, words=words, feedback=feedback or Feedback(provider="offline"), error=error,
    )


def test_round_trip(tmp_path):
    store = Store(tmp_path / "nested" / "coach.db")
    attempt_id = add(store, error="boom")
    attempt = store.get_attempt(attempt_id)
    assert attempt.task_id == "celpip-w1" and attempt.words == 120
    assert attempt.seconds_used == 75 and attempt.error == "boom"
    assert attempt.feedback == Feedback(provider="offline")
    assert attempt.created_at.endswith("+00:00")


def test_missing_attempt_is_none(tmp_path):
    assert Store(tmp_path / "c.db").get_attempt(99) is None


def test_list_is_newest_first_and_filterable_and_limited(tmp_path):
    store = Store(tmp_path / "c.db")
    ids = [add(store, "celpip-w1"), add(store, "ielts-w2"), add(store, "celpip-w1")]
    assert [a.id for a in store.list_attempts()] == ids[::-1]
    assert [a.id for a in store.list_attempts("celpip-w1")] == [ids[2], ids[0]]
    assert len(store.list_attempts(limit=2)) == 2


def test_data_survives_reopening_the_file(tmp_path):
    path = tmp_path / "c.db"
    add(Store(path))
    assert len(Store(path).list_attempts()) == 1
