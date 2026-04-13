#!/usr/bin/env python3

import json
import os
import sys
import time
from datetime import datetime, UTC
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import init_db, get_planted_trees

LAST_RUN_FILE = Path(os.environ.get(
    "GREENBELT_FOREST_STATE",
    Path.home() / ".claude" / "greenbelt_forest.json",
))

GROWTH_STAGES = ["🌱", "🌿", "🌳"]
COLS = 10
DELAY = 0.7


def load_last_run() -> str | None:
    if LAST_RUN_FILE.exists():
        return json.loads(LAST_RUN_FILE.read_text()).get("last_run")
    return None


def save_last_run() -> None:
    LAST_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_RUN_FILE.write_text(json.dumps({"last_run": datetime.now(UTC).isoformat()}))


def forest_lines(old: int, new: int, new_icon: str) -> list[str]:
    """Render the forest grid. Old trees are always 🌳; new trees use new_icon."""
    trees = ["🌳"] * old + [new_icon] * new
    if not trees:
        return ["  (no trees yet — keep coding!)"]
    return [
        "  " + "  ".join(trees[i : i + COLS])
        for i in range(0, len(trees), COLS)
    ]


def animate(out, old: int, new: int, is_tty: bool) -> None:
    if not is_tty or new == 0:
        for line in forest_lines(old, new, "🌳"):
            out.write(line + "\n")
        out.flush()
        return

    for stage_idx, icon in enumerate(GROWTH_STAGES):
        lines = forest_lines(old, new, icon)
        if stage_idx > 0:
            out.write(f"\033[{len(lines)}A")   # move cursor back up
        for line in lines:
            out.write(line + "\n")
        out.flush()
        if stage_idx < len(GROWTH_STAGES) - 1:
            time.sleep(DELAY)


def main() -> None:
    init_db()

    plantings = get_planted_trees()
    last_run = load_last_run()

    old_count = 0
    new_count = 0
    for num_trees, created_at in plantings:
        if last_run and created_at <= last_run:
            old_count += num_trees
        else:
            new_count += num_trees

    total = old_count + new_count
    label = "1 tree" if total == 1 else f"{total} trees"

    # Write animation directly to the terminal so it works even when stdout
    # is captured (e.g. when invoked via a Claude Code slash command).
    try:
        out = open("/dev/tty", "w")
        is_tty = True
    except OSError:
        out = sys.stdout
        is_tty = False

    try:
        out.write(f"\n🌲 Your forest — {label} planted\n\n")
        out.flush()
        animate(out, old_count, new_count, is_tty)
        out.write("\n")
        out.flush()
    finally:
        if out is not sys.stdout:
            out.close()

    save_last_run()


if __name__ == "__main__":
    main()
