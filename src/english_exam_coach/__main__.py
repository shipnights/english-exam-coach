"""Run the app: `python -m english_exam_coach` or `english-exam-coach`."""

from __future__ import annotations

import argparse

import uvicorn

from .app import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="English Exam Coach, a local practice coach.")
    parser.add_argument("--host", default="127.0.0.1", help="Interface to bind. Keep the default for personal use.")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(create_app(), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
