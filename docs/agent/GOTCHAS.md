# Gotchas

- `api/secrets.php` holds live production credentials: edit manually only. A PreToolUse hook blocks agent edits (Claude `block-creds-edit`, Codex project hook).
- A debug script was once deployed by mistake; deploy commands containing diag/debug/test are blocked by hook.
- Forgetting the `?v=` bump leaves returning visitors on stale JS/CSS for up to 30 days.
- `.planning/`, `instagram-media/`, `screenshots/`, `.playwright-mcp/`, and SEO cache dirs are git-ignored scratch.
- `OpenMontage/` is untracked and large; do not commit it or search it for site code.
- Live SEO worktrees exist on this machine with local `.codex/hooks.json` copies; new worktrees need the hook wired.
- Google data lags 2-3 days; Clarity allows about 10 calls per day.
- Claims in copy (reviews, guest counts) are owner-supplied and unverifiable from the repo.
- Agent config layout: `.claude/` holds the real skills (none are shared with Codex, so no `.agents/` folder). `.codex/hooks.json` is kept (Codex-only hook, Claude uses `.claude/settings.local.json`). `AGENTS.md` is the single instruction file; `CLAUDE.md` is `@AGENTS.md`.
