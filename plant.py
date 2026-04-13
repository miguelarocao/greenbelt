#!/usr/bin/env python3

import os
import sys
import tomllib
import uuid
from datetime import datetime, UTC
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import init_db, add_trees, get_total_trees
from providers import PROVIDERS, KEYLESS_PROVIDERS

CONFIG_PATH = Path(os.environ.get("GREENBELT_CONFIG", Path.home() / ".claude" / "greenbelt.toml"))


def main() -> None:
    if not CONFIG_PATH.exists():
        print("[greenbelt] No config found. Run a Claude Code session first to create it.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(CONFIG_PATH, "rb") as f:
            config = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(f"[greenbelt] Failed to parse config: {e}", file=sys.stderr)
        sys.exit(1)

    init_db()

    provider = config["provider"]
    plant_fn = PROVIDERS.get(provider)
    if plant_fn is None:
        print(f"[greenbelt] Unsupported provider: {provider}", file=sys.stderr)
        sys.exit(1)

    api_key = config.get(provider, {}).get("api_key", "")
    if provider not in KEYLESS_PROVIDERS and not api_key:
        print(f"[greenbelt] Warning: {provider}.api_key is blank", file=sys.stderr)
        sys.exit(1)

    try:
        plant_fn(api_key, 1, idempotency_key=str(uuid.uuid4()))
    except Exception as e:
        print(f"[greenbelt] Failed to plant tree: {e}", file=sys.stderr)
        sys.exit(1)

    add_trees(
        used_tokens=0,
        num_trees=1,
        provider=provider,
        timestamp=datetime.now(UTC),
    )

    total = get_total_trees()
    label = "1 tree" if total == 1 else f"{total} trees"
    print(f"🌳 Tree planted! You've now planted {label} in total.")


if __name__ == "__main__":
    main()
