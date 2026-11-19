"""The local web app. It serves one learner on their own machine and has no accounts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .checks import measured_checks
from .config import Settings, load_settings
from .feedback import Feedback, FeedbackError, FeedbackProvider, build_provider
from .metrics import analyze, target_status
from .prompts import get_prompt, random_prompt
from .store import Attempt, Store
from .tasks import TASKS, find_task, tasks_by_track

PACKAGE_DIR = Path(__file__).parent
MAX_RESPONSE_CHARS = 20_000


def _score_range(feedback: Feedback) -> str:
    if feedback.overall_low is None or feedback.overall_high is None:
        return ""
    if feedback.overall_low == feedback.overall_high:
        return f"{feedback.overall_low:g}"
    return f"{feedback.overall_low:g} to {feedback.overall_high:g}"


def _attempt_json(attempt: Attempt) -> dict[str, Any]:
    return {
        "id": attempt.id,
        "created_at": attempt.created_at,
        "task_id": attempt.task_id,
        "prompt_id": attempt.prompt_id,
        "seconds_used": attempt.seconds_used,
        "words": attempt.words,
        "estimated_range": _score_range(attempt.feedback),
        "provider": attempt.feedback.provider,
        "error": attempt.error,
    }


def create_app(
    settings: Settings | None = None,
    provider: FeedbackProvider | None = None,
    store: Store | None = None,
) -> FastAPI:
    settings = settings or load_settings()
    store = store or Store(settings.db_path)
    provider = provider or build_provider(settings)

    app = FastAPI(title="English Exam Coach", docs_url=None, redoc_url=None, openapi_url=None)
    app.mount("/static", StaticFiles(directory=PACKAGE_DIR / "static"), name="static")
    templates = Jinja2Templates(directory=PACKAGE_DIR / "templates")
    templates.env.globals["provider_name"] = provider.name
    templates.env.filters["g"] = lambda value: f"{value:g}"
    templates.env.filters["score_range"] = _score_range

    def render_write(request: Request, task, prompt, text: str = "", error: str = "", status: int = 200):
        return templates.TemplateResponse(
            request, "write.html", {"task": task, "prompt": prompt, "text": text, "error": error},
            status_code=status,
        )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    def index(request: Request):
        return templates.TemplateResponse(
            request, "index.html",
            {"groups": tasks_by_track(), "recent": store.list_attempts(limit=5)},
        )

    @app.get("/write/{task_id}")
    def write(request: Request, task_id: str, prompt: str | None = None):
        task = find_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Unknown task.")
        chosen = get_prompt(prompt) if prompt else random_prompt(task_id)
        if chosen is None or chosen.task_id != task.id:
            raise HTTPException(status_code=404, detail="Unknown prompt for this task.")
        return render_write(request, task, chosen)

    @app.post("/submit")
    def submit(
        request: Request,
        task_id: str = Form(...),
        prompt_id: str = Form(...),
        response_text: str = Form(""),
        seconds_used: int = Form(0),
    ):
        task = find_task(task_id)
        prompt = get_prompt(prompt_id)
        if task is None or prompt is None or prompt.task_id != task.id:
            raise HTTPException(status_code=404, detail="Unknown task or prompt.")

        text = response_text.strip()
        if len(text) > MAX_RESPONSE_CHARS:
            return render_write(
                request, task, prompt, text=response_text,
                error=f"That is too long. The limit is {MAX_RESPONSE_CHARS:,} characters.", status=400,
            )
        metrics = analyze(text)
        if metrics.words == 0:
            return render_write(
                request, task, prompt, text=response_text, error="Write something before submitting.",
                status=400,
            )

        error = ""
        try:
            feedback = provider.evaluate(task, prompt.text, text, metrics)
        except FeedbackError as exc:
            feedback = Feedback(provider=provider.name)
            error = str(exc)

        attempt_id = store.add_attempt(
            task_id=task.id, prompt_id=prompt.id, prompt_text=prompt.text, response_text=text,
            seconds_used=max(0, seconds_used), words=metrics.words, feedback=feedback, error=error,
        )
        return RedirectResponse(f"/attempts/{attempt_id}", status_code=303)

    @app.get("/attempts/{attempt_id}")
    def attempt_page(request: Request, attempt_id: int):
        attempt = store.get_attempt(attempt_id)
        task = find_task(attempt.task_id) if attempt else None
        if attempt is None or task is None:
            raise HTTPException(status_code=404, detail="No such attempt.")
        metrics = analyze(attempt.response_text)
        return templates.TemplateResponse(
            request, "attempt.html",
            {
                "attempt": attempt, "task": task, "metrics": metrics,
                "checks": measured_checks(metrics, task),
                "length_status": target_status(metrics.words, task.min_words, task.max_words),
                "prompt": get_prompt(attempt.prompt_id),
            },
        )

    @app.get("/progress")
    def progress(request: Request):
        attempts = store.list_attempts(limit=200)
        rows = []
        for task in TASKS:
            mine = [a for a in attempts if a.task_id == task.id]
            if not mine:
                continue
            latest_scored = next((a for a in mine if a.feedback.has_scores), None)
            rows.append(
                {
                    "task": task,
                    "count": len(mine),
                    "avg_words": round(sum(a.words for a in mine) / len(mine)),
                    "latest_range": _score_range(latest_scored.feedback) if latest_scored else "",
                }
            )
        return templates.TemplateResponse(
            request, "progress.html", {"rows": rows, "attempts": attempts, "tasks": {t.id: t for t in TASKS}},
        )

    @app.get("/api/attempts")
    def api_attempts() -> JSONResponse:
        return JSONResponse([_attempt_json(a) for a in store.list_attempts(limit=200)])

    return app
