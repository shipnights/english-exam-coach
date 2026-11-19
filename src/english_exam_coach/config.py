"""Settings read from the environment. Every value has a safe local default."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MODEL = "claude-sonnet-5-5"
PROVIDERS = ("offline", "anthropic")


class ConfigError(ValueError):
    """Raised when the environment describes a setup that cannot work."""


@dataclass(frozen=True)
class Settings:
    db_path: Path
    provider: str
    anthropic_api_key: str
    model: str


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build Settings from `env` (defaults to os.environ)."""
    env = os.environ if env is None else env
    key = env.get("ANTHROPIC_API_KEY", "").strip()
    provider = env.get("EEC_PROVIDER", "").strip().lower() or ("anthropic" if key else "offline")
    if provider not in PROVIDERS:
        raise ConfigError(f"EEC_PROVIDER must be one of {', '.join(PROVIDERS)}; got {provider!r}.")
    if provider == "anthropic" and not key:
        raise ConfigError("EEC_PROVIDER=anthropic needs ANTHROPIC_API_KEY to be set.")
    db_path = Path(env.get("EEC_DB_PATH", "").strip() or "data/coach.db")
    model = env.get("EEC_MODEL", "").strip() or DEFAULT_MODEL
    return Settings(db_path=db_path, provider=provider, anthropic_api_key=key, model=model)
