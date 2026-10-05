# Weekly SEO v2 Completion Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the remaining weekly SEO v2 data collection and proposal workflow without inventing measurements or business facts.

**Architecture:** Keep source-specific collection in `.claude/seo/`; normalize each result to the existing metrics shape and track unavailable checks in `coverage.json`. Use existing GSC, Bing, GA4 and Clarity bundles for query selection. Keep copy, booking and other Tier 2 changes on proposal branches for review.

**Tech Stack:** Python 3 standard library, shell, unittest, existing site files.

**Spec:** `docs/superpowers/specs/2026-10-02-weekly-seo-v2-design.md`

## Global Constraints

- No invented ratings, prices, distances, ranks, AI mentions, or account observations.
- The booking probe performs GET requests only and never reaches order or payment endpoints.
- Missing credentials, login gates and absent data produce explicit coverage gaps, not zeros.
- No new website build step or dependency.
- Keep site-facing factual edits separate from the SEO automation.

## Review Focus

- Missing or stale GSC/Bing data selects a recorded fallback query set and marks it stale.
- An API or HTTP error stays visible in metrics and coverage.
- A failed booking probe never performs a POST or creates an order.
- A Tier 2 proposal cannot land on `main` without a per-item decision.
- Unverified property claims do not enter page copy or structured data.

---

### Task 1: Query discovery and rank evidence

**Files:** `.claude/seo/query_discovery.py`, `.claude/seo/tests/test_query_discovery.py`, `.claude/seo/extract-all.sh`, `.claude/seo/coverage_ledger.py`

- [ ] Add failing tests for query classification, scoring, stable core rotation, fallback, and evidence fields.
- [ ] Run tests and confirm expected failures.
- [ ] Implement selection from existing bundles and wire it after normalization.
- [ ] Run the full SEO suite and record the result.

### Task 2: Additional read-only checks

**Files:** `.claude/seo/booking_probe.py`, `.claude/seo/tests/test_booking_probe.py`, `.claude/seo/coverage_ledger.py`, `.claude/seo/extract-all.sh`, source references.

- [ ] Add failing tests for GET-only requests, redirects, latency, non-200 results, and exception handling.
- [ ] Implement the booking probe and expose explicit coverage states for Hostinger, listing/reviews, Bing UI links and AI mentions where automated access is unavailable.
- [ ] Run tests and check metrics shape.

### Task 3: Tier 2 proposals and site facts

**Files:** `.claude/seo/ledger.py` or a small companion script, tests, weekly SEO references, affected HTML/blog files.

- [ ] Add failing tests for a proposal record tied to a verified finding and for main-branch protection.
- [ ] Implement proposal preparation without applying facts or booking edits to `main`.
- [ ] Remove or qualify unsupported property claims where the owner has no confirmed values; verify visible copy and JSON-LD agree.
- [ ] Run relevant tests and the site verification script.

### Task 4: Delivery and operational checks

- [ ] Review the four untracked SEO files; commit durable research, exclude disposable raw capture.
- [ ] Check current live status of deployed pages and available account signals; record evidence and unresolved account gates.
- [ ] Run final tests, skill gate, site checks, diff review, and independent Claude review.
- [ ] Fast-forward the completion branch to `main`, clean merged worktrees, and sync Git if verification and access permit.
