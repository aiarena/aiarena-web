"""Live-updating Discord card for a GitHub Actions workflow run.

Polls the Actions API every few seconds, renders a card with one row per
configured job, and PATCHes a single Discord webhook message. Exits when
every watched job is in a terminal state.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml


POLL_INTERVAL_SECONDS = 5
MAX_POLL_DURATION_SECONDS = 6 * 60 * 60  # safety cap; workflow timeout is the real bound

STATE_EMOJI = {
    ("queued", None): "⏸️",
    ("pending", None): "⏸️",
    ("waiting", None): "🕓",
    ("in_progress", None): "⏳",
    ("completed", "success"): "✅",
    ("completed", "failure"): "❌",
    ("completed", "cancelled"): "🚫",
    ("completed", "skipped"): "⏭️",
    ("completed", "timed_out"): "⏱️",
    ("completed", "action_required"): "⚠️",
    ("completed", "neutral"): "⚪",
    ("completed", "stale"): "🪦",
}
UNKNOWN_EMOJI = "❔"
MISSING_EMOJI = "⏸️"  # row in config but not yet in API response

TERMINAL_CONCLUSIONS = {
    "success",
    "failure",
    "cancelled",
    "skipped",
    "timed_out",
    "action_required",
    "neutral",
    "stale",
}

COLOR_RUNNING = 0xC69026
COLOR_SUCCESS = 0x57AB5A
COLOR_FAILURE = 0xE5534B
COLOR_CANCELLED = 0x9198A1


def load_config(path: Path) -> list[dict]:
    with path.open() as f:
        data = yaml.safe_load(f)
    return data["jobs"]


def gh_api(path: str, token: str) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def fetch_jobs(repo: str, run_id: str, token: str) -> list[dict]:
    jobs: list[dict] = []
    page = 1
    while True:
        data = gh_api(
            f"/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100&page={page}",
            token,
        )
        jobs.extend(data.get("jobs", []))
        if len(jobs) >= data.get("total_count", 0):
            break
        page += 1
    return jobs


def fetch_run(repo: str, run_id: str, token: str) -> dict[str, Any]:
    return gh_api(f"/repos/{repo}/actions/runs/{run_id}", token)


def pick_emoji(status: str | None, conclusion: str | None) -> str:
    if status is None:
        return MISSING_EMOJI
    if status == "completed":
        return STATE_EMOJI.get(("completed", conclusion), UNKNOWN_EMOJI)
    return STATE_EMOJI.get((status, None), UNKNOWN_EMOJI)


def is_terminal(job: dict) -> bool:
    if job.get("status") != "completed":
        return False
    return job.get("conclusion") in TERMINAL_CONCLUSIONS


def overall_color(watched_states: list[tuple[str | None, str | None]]) -> int:
    statuses = [s for s, _ in watched_states]
    conclusions = [c for s, c in watched_states if s == "completed"]
    if any(c == "failure" for c in conclusions):
        return COLOR_FAILURE
    if all(s == "completed" for s in statuses):
        if all(c in ("success", "skipped", "neutral") for c in conclusions):
            return COLOR_SUCCESS
        if any(c == "cancelled" for c in conclusions):
            return COLOR_CANCELLED
        return COLOR_SUCCESS
    return COLOR_RUNNING


def render_embed(
    config: list[dict],
    jobs_by_name: dict[str, dict],
    run: dict,
    repo: str,
) -> dict[str, Any]:
    rows: list[str] = []
    watched_states: list[tuple[str | None, str | None]] = []
    for entry in config:
        label = entry["label"]
        job = jobs_by_name.get(entry["name"])
        if job is None:
            rows.append(f"{MISSING_EMOJI} {label}")
            watched_states.append((None, None))
            continue
        emoji = pick_emoji(job.get("status"), job.get("conclusion"))
        url = job.get("html_url") or run.get("html_url")
        rows.append(f"{emoji} [{label}]({url})")
        watched_states.append((job.get("status"), job.get("conclusion")))

    head_commit = run.get("head_commit") or {}
    sha = (run.get("head_sha") or "")[:7]
    author = (head_commit.get("author") or {}).get("name") or run.get("triggering_actor", {}).get("login") or "unknown"
    msg_line = (head_commit.get("message") or "").splitlines()[0] if head_commit.get("message") else ""
    branch = run.get("head_branch") or "?"
    repo_short = repo.split("/")[-1]

    title = f"[{repo_short}:{branch}] CI · run #{run.get('run_number', '?')}"
    footer_bits = [sha, author]
    if msg_line:
        footer_bits.append(msg_line[:80])
    footer = " · ".join(b for b in footer_bits if b)

    return {
        "title": title,
        "url": run.get("html_url"),
        "color": overall_color(watched_states),
        "description": "\n".join(rows),
        "footer": {"text": footer},
    }


DISCORD_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "aiarena-notify-discord (+https://github.com/aiarena/aiarena-web)",
}


def discord_post(webhook: str, embed: dict) -> str:
    body = json.dumps({"embeds": [embed]}).encode()
    req = urllib.request.Request(
        f"{webhook}?wait=true",
        data=body,
        headers=DISCORD_HEADERS,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["id"]


def discord_patch(webhook: str, message_id: str, embed: dict) -> None:
    body = json.dumps({"embeds": [embed]}).encode()
    req = urllib.request.Request(
        f"{webhook}/messages/{message_id}",
        data=body,
        headers=DISCORD_HEADERS,
        method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()


def main() -> int:
    webhook = os.environ["DISCORD_WEBHOOK"]
    repo = os.environ["GITHUB_REPOSITORY"]
    run_id = os.environ["GITHUB_RUN_ID"]
    token = os.environ.get("GITHUB_TOKEN", "")
    config_path = Path(os.environ.get("NOTIFY_DISCORD_CONFIG", ".github/notify-discord.yml"))

    config = load_config(config_path)
    deadline = time.monotonic() + MAX_POLL_DURATION_SECONDS

    run = fetch_run(repo, run_id, token)
    jobs = fetch_jobs(repo, run_id, token)
    jobs_by_name = {j["name"]: j for j in jobs}
    embed = render_embed(config, jobs_by_name, run, repo)
    message_id = discord_post(webhook, embed)

    last_payload = json.dumps(embed, sort_keys=True)

    while time.monotonic() < deadline:
        time.sleep(POLL_INTERVAL_SECONDS)
        run = fetch_run(repo, run_id, token)
        jobs = fetch_jobs(repo, run_id, token)
        jobs_by_name = {j["name"]: j for j in jobs}
        embed = render_embed(config, jobs_by_name, run, repo)
        payload = json.dumps(embed, sort_keys=True)
        if payload != last_payload:
            discord_patch(webhook, message_id, embed)
            last_payload = payload

        watched_terminal = all(
            (j := jobs_by_name.get(entry["name"])) is not None and is_terminal(j) for entry in config
        )
        if watched_terminal:
            return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
