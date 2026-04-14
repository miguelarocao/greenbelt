import json
import os
from datetime import datetime, UTC
from pathlib import Path

LOCAL_FILE = Path(os.environ.get("GREENBELT_LOCAL_FILE", Path.home() / ".claude" / "greenbelt_local.json"))


def plant_trees(api_key: str, number: int, *, idempotency_key: str) -> None:
    """Local file-based tree planting for testing (no API calls)."""
    records = []
    if LOCAL_FILE.exists():
        with open(LOCAL_FILE, "r") as f:
            records = json.load(f)

    # Honour idempotency: skip if we've already recorded this key
    if any(r.get("idempotency_key") == idempotency_key for r in records):
        return

    records.append({
        "idempotency_key": idempotency_key,
        "number": number,
        "planted_at": datetime.now(UTC).isoformat(),
    })

    LOCAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCAL_FILE, "w") as f:
        json.dump(records, f, indent=2)
