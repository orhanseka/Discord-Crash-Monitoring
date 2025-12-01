# DC Crash Monitor

Python-based macOS monitoring tool tailored to keep an eye on Discord-connected data servers.
It keeps a local crash/bug log, surfaces summaries, and can optionally forward alerts to Discord via webhooks.

## Features

- polls Discord servers with provided tokens to capture basic stats (member count, online status)
- records crash or bug alerts with severity, origin, and timestamps into a local SQLite store
- provides CLI commands to log incidents, list recent entries, and show daily aggregates
- optional webhook forwarding keeps a Discord channel informed immediately

## Requirements

- Python 3.11+
- Dependencies listed in `requirements.txt`

## Setup

1. `python -m venv .venv && . .venv/bin/activate`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill your Discord token, guild id, and optional webhook URL.

## Usage examples

```bash
python -m crash_monitor monitor --config .env
python -m crash_monitor log --severity high --title "Crash on sync" --details "stack overflow at sync" --origin "sync-service"
python -m crash_monitor summary --days 7
```

The CLI also exposes `discord:info` to fetch server statistics and `webhook:send` for testing the notification flow.

## Commands

Command-line entry point is `python -m crash_monitor`. The following subcommands help you log and inspect incidents:

- `log` – record an incident with required `--severity` and `--title`, plus optional `--details`, `--origin`, and `--metadata`.
- `recent` – show the latest incidents (`--limit` defaults to 10).
- `summary` – summarize incidents grouped by severity for the last `--days` window (default 7).
- `discord-info` – query Discord for the configured guild snapshot (requires `DISCORD_TOKEN` and `GUILD_ID`).
- `webhook-send` – send a test payload to `INCIDENT_WEBHOOK` to verify Discord notifications.
- `monitor` – print the guild snapshot, a short summary, and the latest few incidents for quick situational awareness.

## Convenience script

Run [`./run_monitor.sh`](./run_monitor.sh) to create/activate the virtual environment, install dependencies, and invoke the CLI. Pass any subcommand you like as arguments; without arguments it defaults to `monitor`.
