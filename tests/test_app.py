import pytest
from fastapi.testclient import TestClient

from english_exam_coach.app import create_app
from english_exam_coach.config import Settings
from english_exam_coach.feedback import CriterionScore, Feedback, FeedbackError, OfflineProvider
from english_exam_coach.store import Store

ESSAY = " ".join(["Remote work gives people flexibility, but offices build trust between colleagues."] * 4)


class StubProvider:
    name = "stub"

    def __init__(self, error=None):
        self.error, self.seen = error, []

    def evaluate(self, task, prompt_text, response_text, metrics):
        self.seen.append((task.id, response_text))
        if self.error:
            raise FeedbackError(self.error)
        return Feedback(
            provider=self.name,
            criteria=tuple(CriterionScore(name, 6.5, f"{name} comment") for name in task.criteria),
            overall_low=6.0, overall_high=7.0,
            strengths=("Clear position",), improvements=("Vary vocabulary",),
            revised_paragraph="A tighter paragraph.",
        )


def make_client(tmp_path, provider):
    settings = Settings(tmp_path / "t.db", "offline", "", "m")
    app = create_app(settings, provider=provider, store=Store(settings.db_path))
    return TestClient(app)


@pytest.fixture
def client(tmp_path):
    return make_client(tmp_path, StubProvider())


def submit(client, **overrides):
    data = {"task_id": "ielts-w2", "prompt_id": "ielts-w2-remote", "response_text": ESSAY, "seconds_used": "90"}
    data.update(overrides)
    return client.post("/submit", data=data, follow_redirects=False)


def test_health_and_index(client):
    assert client.get("/healthz").json() == {"status": "ok"}
    page = client.get("/")
    assert page.status_code == 200
    assert "IELTS-style" in page.text and "CELPIP-style" in page.text and "/write/celpip-w1" in page.text


def test_write_page_shows_the_prompt_table_and_timer_hooks(client):
    page = client.get("/write/ielts-w1?prompt=ielts-w1-cafe")
    assert page.status_code == 200
    assert "Cold drinks" in page.text and 'id="write-form"' in page.text
    assert 'data-min-words="150"' in page.text and "data-max-words" not in page.text


def test_write_without_a_prompt_picks_one_for_that_task(client):
    page = client.get("/write/celpip-w2")
    assert page.status_code == 200 and "Option A" in page.text


@pytest.mark.parametrize("path", ["/write/nope", "/write/ielts-w2?prompt=celpip-w1-dog", "/write/ielts-w2?prompt=zzz"])
def test_unknown_task_or_mismatched_prompt_is_404(client, path):
    assert client.get(path).status_code == 404


def test_submit_scores_stores_and_redirects_to_the_attempt(client):
    response = submit(client)
    assert response.status_code == 303 and response.headers["location"] == "/attempts/1"

    page = client.get("/attempts/1")
    assert page.status_code == 200
    assert "Estimated band: 6 to 7" in page.text
    assert "Task Response comment" in page.text and "A tighter paragraph." in page.text
    assert "Measured checks" in page.text and "Too short" in page.text
    assert "1:30 used of 40:00" in page.text


def test_learner_text_is_escaped_everywhere(client):
    attack = "<script>alert(1)</script> " + ESSAY
    assert submit(client, response_text=attack).status_code == 303
    page = client.get("/attempts/1").text
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page


def test_empty_submission_is_rejected_and_not_stored(client):
    response = submit(client, response_text="   ")
    assert response.status_code == 400 and "Write something" in response.text
    assert client.get("/api/attempts").json() == []


def test_oversized_submission_is_rejected(client):
    response = submit(client, response_text="word " * 5000)
    assert response.status_code == 400 and "too long" in response.text


def test_bad_task_or_prompt_on_submit_is_404(client):
    assert submit(client, task_id="nope").status_code == 404
    assert submit(client, prompt_id="celpip-w1-dog").status_code == 404


def test_negative_time_is_stored_as_zero(client):
    submit(client, seconds_used="-50")
    assert client.get("/api/attempts").json()[0]["seconds_used"] == 0


def test_provider_failure_still_saves_the_attempt_with_a_clear_message(tmp_path):
    client = make_client(tmp_path, StubProvider(error="The feedback request failed (RateLimitError)."))
    assert submit(client).status_code == 303
    page = client.get("/attempts/1").text
    assert "Scored feedback was not available" in page and "RateLimitError" in page
    assert "Measured checks" in page and "Estimated band" not in page


def test_offline_mode_shows_banner_and_no_scores(tmp_path):
    client = make_client(tmp_path, OfflineProvider())
    assert "Offline mode" in client.get("/").text
    submit(client)
    page = client.get("/attempts/1").text
    assert "Measured checks" in page and "Estimated band" not in page


def test_missing_attempt_is_404(client):
    assert client.get("/attempts/42").status_code == 404


def test_progress_summarises_attempts(client):
    assert "No attempts yet" in client.get("/progress").text
    submit(client)
    submit(client, task_id="celpip-w1", prompt_id="celpip-w1-dog", response_text="Dear neighbour, hello.")
    page = client.get("/progress").text
    assert "IELTS-style: Essay" in page and "CELPIP-style: Write an email" in page
    assert "6 to 7" in page

    rows = client.get("/api/attempts").json()
    assert [r["id"] for r in rows] == [2, 1]
    assert rows[1]["estimated_range"] == "6 to 7" and rows[1]["provider"] == "stub"
