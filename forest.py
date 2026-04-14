#!/usr/bin/env python3

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import init_db, get_total_trees

COLS = 10


def forest_lines(total: int) -> list[str]:
    if not total:
        return ["  (no trees yet — keep coding!)"]
    trees = ["🌳"] * total
    return [
        "  " + "  ".join(trees[i : i + COLS])
        for i in range(0, len(trees), COLS)
    ]


def main() -> None:
    init_db()

    total = get_total_trees()
    label = "1 tree" if total == 1 else f"{total} trees"

    sys.stdout.write(f"\n🌲 Your forest — {label} planted\n\n")
    for line in forest_lines(total):
        sys.stdout.write(line + "\n")
    sys.stdout.write("\n")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
