# Greenbelt 🌱

Greenbelt tracks token usage across Claude Code sessions and plants trees whenever your token usage crosses a configurable threshold (1M tokens by default). It uses the [Ecologi API](https://ecologi.com/) and runs as a Claude Code hook — no manual steps required after setup.

[Ecologi](https://ecologi.com) is a climate action platform that helps individuals and businesses take measurable, credible action for climate and nature. Fund tree planting from €0.80 (£0.60) per tree.

## Get started

**1. Clone the repo**

```bash
git clone https://github.com/miguelarocao/greenbelt ~/.claude/greenbelt
```

**2. Open Claude Code in the repo**

```bash
claude ~/.claude/greenbelt
```

The repo ships with `.claude/settings.json` pre-configured — hooks activate immediately with no manual setup.

**3. Configure your API key**

On the first run, Greenbelt creates `~/.claude/greenbelt.toml` automatically:

```toml
provider = "ecologi"
# provider = "local"  # file-based, no API key needed (good for local testing)
threshold = 1_000_000   # plant a tree every 1M tokens

[ecologi]
api_key = ""            # get it from https://app.ecologi.com/impact-api
```

Fill in your [Ecologi API key](https://app.ecologi.com/impact-api). Adjust `threshold` to control how often trees are planted. Set `provider = "local"` to test without making real API calls — planting records are written to `~/.claude/greenbelt_local.json` instead.

**That's it.** Greenbelt runs silently in the background. At the start of each session it shows how many trees you've planted so far, and prints a green notification whenever a tree is planted.

## Use in all projects

To track tokens across every project (not just when working in the greenbelt directory), add the hooks to your user-level Claude Code settings at `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [{ "type": "command", "command": "python3 ~/.claude/greenbelt/session_hook.py" }]
      }
    ],
    "Stop": [
      {
        "hooks": [{ "type": "command", "command": "python3 ~/.claude/greenbelt/session_hook.py" }]
      }
    ]
  }
}
```

## Commands

To make `/forest` and `/plant` available in all projects, symlink the command files to your user commands directory:

```bash
ln -sf ~/.claude/greenbelt/.claude/commands/forest.md ~/.claude/commands/forest.md
ln -sf ~/.claude/greenbelt/.claude/commands/plant.md ~/.claude/commands/plant.md
```

### /forest

Displays all your planted trees as a grid. Trees planted since the last time you ran `/forest` animate through 🌱 → 🌿 → 🌳; previously seen trees appear immediately as 🌳.

### /plant

Manually plants a tree. Asks for confirmation first — only an exact `yes` proceeds.

## Uninstall

1. **Remove the hooks** from `~/.claude/settings.json` (and the project-level `.claude/settings.json` if you modified it).

2. **Remove command symlinks** (if created):

```bash
rm ~/.claude/commands/forest.md ~/.claude/commands/plant.md
```

3. **Delete the data files**:

```bash
rm ~/.claude/greenbelt.sqlite3 ~/.claude/greenbelt.toml
```

4. **Delete the repo** (optional):

```bash
rm -rf ~/.claude/greenbelt
```

## In Action
<img width="972" height="497" alt="Screenshot 2026-03-18 at 11 43 08" src="https://github.com/user-attachments/assets/5eb23510-253b-44a7-845e-27764aefa004" />

### Gallery

Add your badge here if you use Greenbelt.

![Ecologi](https://api.ecologi.com/badges/trees/69b932ffb5241f46d9b8e6c8?black=true&treeOnly=true)
