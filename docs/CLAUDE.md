# Website Project Configuration

## Second Brain: Obsidian Vault

All project outputs and memories are stored in the Obsidian vault for persistence across sessions.

**Vault location**: ~/ObsidianVaults/wiki/projects/Website/

### File Routing Rules

When creating files during this session:

1. **Code files, scripts, outputs** → `~/ObsidianVaults/wiki/projects/Website/outputs/`
2. **Memory, decisions, learnings** → `~/ObsidianVaults/wiki/projects/Website/memory/`
3. **Generated code snippets** → `~/ObsidianVaults/wiki/projects/Website/code/`
4. **Research & findings** → `~/ObsidianVaults/wiki/projects/Website/research/`

### Memory System

Memory is auto-injected at session start. Files in `memory/` persist across `/clear` resets.

To add memory:
```markdown
---
name: kebab-case-slug
type: user|feedback|project|reference
description: One line summary
---

Content here.
```

Link memories with `[[name-slug]]` and update `MEMORY.md`.

### Project Context

See memory files for:
- Current requirements and goals
- Validated approaches (feedback type)
- Ongoing initiatives and deadlines
- External references (Linear, Slack, etc.)

---

## Setup Status

✓ Vault-only routing enabled
✓ SessionStart memory injection active
✓ PostToolUse capture configured
✓ Project memory directory created

Next step: Save context from this session to `memory/` as first memory entry.
