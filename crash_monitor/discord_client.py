from __future__ import annotations

from typing import Any

import requests
from requests import HTTPError

API_BASE = "https://discord.com/api"


def fetch_guild_info(token: str, guild_id: str) -> dict[str, Any]:
    if not token or not guild_id:
        raise ValueError("DISCORD_TOKEN and GUILD_ID must be set to fetch guild info")

    headers = {"Authorization": f"Bot {token}"}
    resp = requests.get(f"{API_BASE}/guilds/{guild_id}", headers=headers, params={"with_counts": "true"}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def send_webhook(url: str, payload: dict[str, Any]) -> None:
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
