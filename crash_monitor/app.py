from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pendulum
from rich.console import Console
from rich.table import Table

from crash_monitor.config import load_config
from crash_monitor.discord_client import fetch_guild_info, send_webhook
from crash_monitor.store import CrashStore

console = Console()


def display_recent(store: CrashStore, limit: int = 10) -> None:
    records = store.list_recent(limit)
    table = Table(title="Recent Incidents")
    table.add_column("Time", style="cyan")
    table.add_column("Severity")
    table.add_column("Title")
    table.add_column("Origin", style="magenta")
    table.add_column("Details")

    for row in records:
        ts = pendulum.parse(row[1])
        table.add_row(ts.to_datetime_string(), row[2], row[3], row[5] or "-", (row[4] or "-")[:60])

    console.print(table)


def display_summary(store: CrashStore, days: int) -> None:
    summary = store.summary(days=days)
    table = Table(title=f"Incident Summary ({days}d)")
    table.add_column("Severity")
    table.add_column("Count", justify="right")
    if not summary:
        console.print("No incidents recorded within the requested range.")
        return

    for row in summary:
        table.add_row(row["severity"], str(row["total"]))
    console.print(table)


def handle_discord_info(token: str, guild_id: str) -> None:
    info = fetch_guild_info(token, guild_id)
    table = Table(title="Discord Guild Snapshot")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Name", info.get("name", "-"))
    table.add_row("Members", str(info.get("approximate_member_count", "-")))
    table.add_row("Online", str(info.get("approximate_presence_count", "-")))
    table.add_row("Guild ID", info.get("id", "-"))
    console.print(table)


def handle_webhook(url: str, payload: dict[str, Any]) -> None:
    send_webhook(url, payload)
    console.print("Webhook delivered successfully.", style="bold green")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m crash_monitor")
    parser.add_argument("--config", default=".env", help="Path to .env file")

    sub = parser.add_subparsers(dest="command", required=True)

    log = sub.add_parser("log", help="Record a crash or bug incident locally")
    log.add_argument("--severity", choices=["low", "medium", "high", "critical"], required=True)
    log.add_argument("--title", required=True)
    log.add_argument("--details", default="")
    log.add_argument("--origin", default="general")
    log.add_argument("--metadata", default="")

    summary = sub.add_parser("summary", help="Show aggregated incidents for the past n days")
    summary.add_argument("--days", type=int, default=7)

    recent = sub.add_parser("recent", help="Show the latest incidents")
    recent.add_argument("--limit", type=int, default=10)

    discord_info = sub.add_parser("discord-info", help="Fetch guild stats from Discord")

    webhook = sub.add_parser("webhook-send", help="Test-send an incident to configured webhook")
    webhook.add_argument("--severity", choices=["low", "medium", "high", "critical"], default="medium")
    webhook.add_argument("--title", default="Test incident")
    webhook.add_argument("--details", default="Routine webhook test from mac monitor")

    monitor = sub.add_parser("monitor", help="Print guild info, incident summary, and recent log")
    monitor.add_argument("--days", type=int, default=1)
    monitor.add_argument("--limit", type=int, default=5)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(Path(args.config))
    store = CrashStore(config.db_path)

    try:
        if args.command == "log":
            store.log_incident(
                severity=args.severity,
                title=args.title,
                details=args.details,
                origin=args.origin,
                metadata=args.metadata,
            )
            console.print("Incident recorded.", style="bold green")
        elif args.command == "summary":
            display_summary(store, args.days)
        elif args.command == "recent":
            display_recent(store, args.limit)
        elif args.command == "discord-info":
            handle_discord_info(config.discord_token, config.guild_id)
        elif args.command == "webhook-send":
            if not config.webhook_url:
                console.print("Set INCIDENT_WEBHOOK to use webhook commands.", style="bold yellow")
            else:
                handle_webhook(
                    config.webhook_url,
                    {
                        "content": f"[{args.severity.upper()}] {args.title}",
                        "embeds": [
                            {"description": args.details, "title": "Crash monitor alert"},
                        ],
                    },
                )
        elif args.command == "monitor":
            if config.discord_token and config.guild_id:
                handle_discord_info(config.discord_token, config.guild_id)
            display_summary(store, args.days)
            display_recent(store, args.limit)
    finally:
        store.close()


if __name__ == "__main__":
    main()
