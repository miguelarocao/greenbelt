#!/usr/bin/env python3

import json
import os
import subprocess
import sys

if sys.version_info < (3, 11):
    print("[greenbelt] Python 3.11+ is required. Install it via Homebrew: brew install python@3.11", file=sys.stderr)
    sys.exit(1)

import tomllib
from datetime import datetime, UTC
from pathlib import Path

from db import init_db
from db import add_trees
from db import add_usage
from db import get_total_trees
from db import get_unaccounted_usage
from providers import PROVIDERS, KEYLESS_PROVIDERS


CONFIG_PATH = Path(os.environ.get("GREENBELT_CONFIG", Path.home() / ".claude" / "greenbelt.toml"))


CONFIG_TEMPLATE = """\
provider = "ecologi"
# provider = "local"  # file-based, no API key needed (good for local testing)
threshold = 1_000_000
[ecologi]
api_key = "" # get it from https://app.ecologi.com/impact-api
"""


def _parse_usage(raw: str) -> int:
    result = 0
    try:
        transcript = json.loads(raw)

        if "totalTokens" in transcript.get("toolUseResult", {}):
            result = transcript["toolUseResult"]["totalTokens"]
        elif transcript["type"] == "assistant":
            usage = transcript["message"]["usage"]
            result = usage["input_tokens"] + usage["output_tokens"]
        elif transcript["type"] == "progress" and transcript["data"]["type"] == "agent_progress" and transcript["data"]["message"]["type"] == "assistant":
            usage = transcript["data"]["message"]["message"]["usage"]
            result = usage["input_tokens"] + usage["output_tokens"]
    except (json.JSONDecodeError, KeyError):
        pass    # ignore

    return result


def calculate_used_tokens(transcript_path: str) -> int:
    used_tokens = 0

    try:
        with open(transcript_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                used_tokens += _parse_usage(line)
    except FileNotFoundError:
        pass    # empty session

    return used_tokens


def calculate_turn_tokens(transcript_path: str) -> int:
    """Count tokens since the last user message (i.e. the current turn only)."""
    lines = []
    try:
        with open(transcript_path, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        return 0

    last_user_idx = -1
    for i, line in enumerate(lines):
        try:
            if json.loads(line).get("type") == "user":
                last_user_idx = i
        except json.JSONDecodeError:
            pass

    return sum(_parse_usage(line) for line in lines[last_user_idx + 1:])


def _tree_message(n: int) -> str:
    label = "a tree" if n == 1 else f"{n} trees"
    return f"\033[92m🌱 You planted {label}!\033[0m"


def print_progress() -> None:
    total_trees = get_total_trees()
    label = "1 tree" if total_trees == 1 else f"{total_trees} trees"
    message = f"🌱 You've planted {label} simply by using Claude Code, helping reduce your CO2 impact!"
    print(f'{{"continue": true, "systemMessage": "{message}"}}')


def handle_stop(config: dict, input_data: dict) -> None:
    used_tokens = calculate_turn_tokens(input_data["transcript_path"])
    if used_tokens == 0:
        return

    add_usage(
        session_id=input_data["session_id"],
        used_tokens=used_tokens,
        timestamp=datetime.now(UTC),
    )

    threshold = config["threshold"]
    unaccounted_usage = get_unaccounted_usage()
    trees_to_plant = unaccounted_usage // threshold
    if trees_to_plant == 0:
        return

    provider = config["provider"]
    plant_fn = PROVIDERS.get(provider)
    if plant_fn is None:
        print(f"[greenbelt] Unsupported provider: {provider}", file=sys.stderr)
        sys.exit(1)

    api_key = config.get(provider, {}).get("api_key", "")
    if provider not in KEYLESS_PROVIDERS and not api_key:
        print(f"[greenbelt] Warning: {provider}.api_key is blank; skipping tree planting", file=sys.stderr)
        sys.exit(1)

    # Idempotency key is unique per planting event: session + trees already planted
    idempotency_key = f"{input_data['session_id']}-{get_total_trees()}"
    try:
        plant_fn(api_key, trees_to_plant, idempotency_key=idempotency_key)
    except Exception as e:
        print(f"[greenbelt] Failed to plant trees: {e}", file=sys.stderr)
        sys.exit(1)

    add_trees(
        used_tokens=trees_to_plant * threshold,
        num_trees=trees_to_plant,
        provider=provider,
        timestamp=datetime.now(UTC),
    )

    print(_tree_message(trees_to_plant), file=sys.stderr)


def handle_prompt_submit(input_data: dict) -> None:
    prompt = input_data.get("prompt", "").strip()
    greenbelt_dir = Path(__file__).parent

    if prompt == "/forest":
        subprocess.run([sys.executable, str(greenbelt_dir / "forest.py")])
        sys.exit(2)

    if prompt == "/plant":
        try:
            with open("/dev/tty", "r+") as tty:
                tty.write("🌱 Plant a tree now? (yes/no) ")
                tty.flush()
                response = tty.readline().strip()
        except OSError:
            sys.exit(0)  # fall back to LLM if no tty

        if response == "yes":
            subprocess.run([sys.executable, str(greenbelt_dir / "plant.py")])
        else:
            sys.stderr.write("Cancelled.\n")
        sys.exit(2)


def main() -> None:
    """
    See https://code.claude.com/docs/en/hooks#common-input-fields
    """
    try:
        if not CONFIG_PATH.exists():
            with open(CONFIG_PATH, "w") as f:
                f.write(CONFIG_TEMPLATE)

        with open(CONFIG_PATH, "rb") as f:
            config = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(f"[greenbelt] Failed to parse config: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"[greenbelt] Failed to parse hook payload: {e}", file=sys.stderr)
        sys.exit(1)

    init_db()

    event = input_data["hook_event_name"]
    if event == "SessionStart":
        print_progress()
    elif event == "Stop":
        handle_stop(config, input_data)
    elif event == "UserPromptSubmit":
        handle_prompt_submit(input_data)


if __name__ == "__main__":
    main()
