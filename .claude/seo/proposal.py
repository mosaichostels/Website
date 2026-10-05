#!/usr/bin/env python3
"""Prepare a verified Tier 2 finding as an unpushed review branch.

Usage: python3 .claude/seo/proposal.py FINDING_ID path/to/reviewed.patch
The patch must be authored and reviewed first. This command applies it only in
an isolated worktree and writes a per-item owner-review note.
"""
import datetime as dt
import pathlib
import re
import subprocess
import sys

import ledger


def _git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args],
                            capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f"git {' '.join(args[:2])} failed: {result.stderr.strip()[:240]}")
    return result.stdout.strip()


def _patch_paths(patch):
    text = pathlib.Path(patch).read_text()
    paths = re.findall(r"^diff --git a/(.+?) b/(.+)$", text, re.M)
    if not paths:
        raise ValueError("patch needs git diff headers")
    result = []
    for before, after in paths:
        if before != after or after.startswith("/") or ".." in pathlib.PurePosixPath(after).parts:
            raise ValueError("renames and paths outside the repo are forbidden")
        low = after.lower()
        if low == "api/secrets.php" or low.startswith((".claude/", "scripts/", ".git/", ".config/")) \
                or low.endswith((".env", ".key", ".pem")):
            raise ValueError(f"forbidden proposal path: {after}")
        result.append(after)
    return result


def prepare(fid, patch, root=ledger.ROOT, reports=ledger.REPORTS, date=None):
    root = pathlib.Path(root).resolve()
    patch = pathlib.Path(patch).resolve()
    date = date or dt.date.today().isoformat()
    finding = ledger._find(ledger.load(reports), fid)
    if finding["status"] != "verified":
        raise ValueError(f"{fid} must be verified before preparing a proposal")
    paths = _patch_paths(patch)
    branch = f"seo/proposals-{date}"
    worktree = root.parent / f"{root.name}-proposals-{date}"
    branches = _git(root, "branch", "--list", branch)
    if branches:
        if not worktree.exists() or _git(worktree, "branch", "--show-current") != branch:
            raise ValueError(f"{branch} exists in another worktree")
    else:
        if worktree.exists():
            raise ValueError(f"proposal worktree path already exists: {worktree}")
        _git(root, "worktree", "add", "-b", branch, str(worktree), "HEAD")
    if _git(worktree, "status", "--porcelain"):
        raise ValueError("proposal worktree has uncommitted changes")
    note = worktree / "seo-reports" / "proposals" / f"{date}-{fid}.md"
    try:
        _git(worktree, "apply", "--check", str(patch))
        _git(worktree, "apply", str(patch))
        _git(worktree, "diff", "--check")
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text(f"# {fid}: {finding['claim']}\n\n"
                        f"Evidence: {finding.get('evidence') or 'See findings ledger'}\n\n"
                        f"Changed paths: {', '.join(paths)}\n\n"
                        "Needs owner approval per item before merging to main.\n"
                        "Branch stays local; no deploy or push is performed.\n")
        verify = worktree / ".claude" / "seo" / "verify.sh"
        if verify.exists():
            result = subprocess.run([str(verify)], cwd=worktree, capture_output=True, text=True)
            if result.returncode:
                raise ValueError(f"site verification failed: {(result.stdout + result.stderr)[-300:]}")
        _git(worktree, "add", "--", *paths, str(note.relative_to(worktree)))
        _git(worktree, "commit", "-m", f"proposal(seo): {fid} {finding['claim'][:55]}")
    except Exception:
        # the worktree was verified clean before apply, so only this proposal's changes are discarded
        _git(worktree, "reset", "--hard", "HEAD")
        _git(worktree, "clean", "-fd", "--", "seo-reports/proposals")
        raise
    return branch, worktree


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    try:
        branch, path = prepare(sys.argv[1], sys.argv[2])
        print(f"{branch} in {path} (local review only)")
    except (ValueError, OSError) as exc:
        sys.exit(f"error: {exc}")
