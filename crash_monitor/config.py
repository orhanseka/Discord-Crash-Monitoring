from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass
class Config:
    discord_token: str
    guild_id: str
    webhook_url: str | None
    db_path: Path


def load_config(env_path: Path | str = ".env") -> Config:
    env_path = Path(env_path)
    if env_path.exists():
        load_dotenv(env_path)
    return Config(
        discord_token=os.environ.get("DISCORD_TOKEN", ""),
        guild_id=os.environ.get("GUILD_ID", ""),
        webhook_url=os.environ.get("INCIDENT_WEBHOOK"),
        db_path=Path(os.environ.get("LOG_DB", "./crash_monitor/db/crashes.sqlite3")),
    )
