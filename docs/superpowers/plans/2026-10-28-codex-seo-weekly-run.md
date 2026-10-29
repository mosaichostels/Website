# Codex SEO Weekly Run Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the existing Codex SEO suite usable by the Mosaic weekly SEO workflow and update the shared skill so Claude and Codex trigger the same run with client-native SEO audits.

**Architecture:** Keep project data extraction and site verification in the existing `.claude/seo` tooling. Use Claude’s existing Google configuration as the source for a Codex-native copy, keep Codex drift state in its own durable cache, and make `.agents/skills/weekly-seo` the shared cross-agent procedure.

**Tech Stack:** Codex SEO `v1.9.6-codex.5`, Python virtualenvs, Markdown skill references, existing shell/Python SEO scripts.

**Spec:** User request in the current conversation.

## Global Constraints

- Never expose credential values or copy them into the repository.
- Preserve unrelated pre-existing working-tree changes.
- Keep the static site free of build steps and dependencies.
- Use Codex’s `seo-*` skills for Codex audits and Claude’s `claude-seo` agents for Claude audits.

## Review Focus

- Codex runtime resolves its own config and virtualenv: verify readiness and Google auth without printing secrets.
- Shared skill commands do not reference obsolete `.Codex` paths or undefined tool variables.
- Audit coverage remains 15 checks and the report ledger ID remains stable.
- Existing uncommitted project changes remain untouched.

### Task 1: Configure and verify Codex SEO

- Confirm the installed release and runtime.
- Mirror the existing Claude Google configuration to `~/.config/codex-seo/google-api.json` with mode 600.
- Create durable separate Codex drift storage and its cache link.
- Verify the Codex environment and Google auth status without exposing credentials.

### Task 2: Synchronize the shared weekly skill

- Update `.agents/skills/weekly-seo/SKILL.md` with the client-native Claude/Codex toolchain and current project paths.
- Synchronize the changed shared references: audit coverage, Common Crawl facts, fix gotchas, and report coverage wording.
- Keep the Codex and Claude project-local copies aligned with the shared version where they are intended as generated/host-specific copies.

### Task 3: Verify project guidance and skill integrity

- Run the skill structure check and relevant SEO unit tests.
- Check for stale `.Codex` references and undefined `$SEO`/`$SEOPY` command variables in the weekly skill.
- Update `docs/agent/STATUS.md` with the setup and verification result.
