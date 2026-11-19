"""Practice history in a single local SQLite file."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .feedback import Feedback

_SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at    TEXT    NOT NULL,
    task_id       TEXT    NOT NULL,
    prompt_id     TEXT    NOT NULL,
    prompt_text   TEXT    NOT NULL,
    response_text TEXT    NOT NULL,
    seconds_used  INTEGER NOT NULL,
    words         INTEGER NOT NULL,
    feedback_json TEXT    NOT NULL,
    error         TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS attempts_task_idx ON attempts (task_id, id);
"""


@dataclass(frozen=True)
class Attempt:
    id: int
    created_at: str
    task_id: str
    prompt_id: str
    prompt_text: str
    response_text: str
    seconds_used: int
    words: int
    feedback: Feedback
    error: str


class Store:
    def __init__(self, path: Path | str) -> None:
        # A file path, not ":memory:": each call opens its own connection.
        self._path = str(path)
        Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as conn, conn:
            conn.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def add_attempt(
        self,
        *,
        task_id: str,
        prompt_id: str,
        prompt_text: str,
        response_text: str,
        seconds_used: int,
        words: int,
        feedback: Feedback,
        error: str = "",
    ) -> int:
        created = datetime.now(UTC).isoformat(timespec="seconds")
        with closing(self._connect()) as conn, conn:
            cursor = conn.execute(
                "INSERT INTO attempts (created_at, task_id, prompt_id, prompt_text, response_text,"
                " seconds_used, words, feedback_json, error) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (created, task_id, prompt_id, prompt_text, response_text, seconds_used, words,
                 json.dumps(feedback.to_dict()), error),
            )
            return int(cursor.lastrowid)

    def get_attempt(self, attempt_id: int) -> Attempt | None:
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT * FROM attempts WHERE id = ?", (attempt_id,)).fetchone()
        return _to_attempt(row) if row else None

    def list_attempts(self, task_id: str | None = None, limit: int = 100) -> list[Attempt]:
        """Newest first."""
        query, params = "SELECT * FROM attempts", []
        if task_id is not None:
            query += " WHERE task_id = ?"
            params.append(task_id)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with closing(self._connect()) as conn:
            rows = conn.execute(query, params).fetchall()
        return [_to_attempt(row) for row in rows]


def _to_attempt(row: sqlite3.Row) -> Attempt:
    return Attempt(
        id=row["id"],
        created_at=row["created_at"],
        task_id=row["task_id"],
        prompt_id=row["prompt_id"],
        prompt_text=row["prompt_text"],
        response_text=row["response_text"],
        seconds_used=row["seconds_used"],
        words=row["words"],
        feedback=Feedback.from_dict(json.loads(row["feedback_json"])),
        error=row["error"],
    )
