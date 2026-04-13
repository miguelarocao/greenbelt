---
allowed_tools: Bash(bash ~/.claude/greenbelt/session_hook.sh)
---

Ask the user: "🌱 Plant a tree now? (yes/no)"

If the response is exactly "yes", run:

```bash
python3 ~/.claude/greenbelt/plant.py
```

Otherwise respond: "Cancelled."
