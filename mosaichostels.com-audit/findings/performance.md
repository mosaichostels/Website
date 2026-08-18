# Performance / Core Web Vitals — mosaichostels.com

**Date:** 2026-08-15 (prior version stale, dated Aug 8; two automated specialist runs stalled before writing — compiled directly via `pagespeed_check.py` PSI Lighthouse mobile runs to avoid a third failed run.)

## Baseline issues — status

| Baseline finding (Aug 8) | Status |
|---|---|
| Unsized footer `<img>` → POOR CLS (0.443) on blog/mobile | **Fixed.** Current CLS: home 0.004, blog post 0.03, book-now 0.003 — all "Good" (<0.1) |
| Missing `<link rel=preconnect>` for Google Fonts (~1,980ms) | **Fixed.** `preconnect` for `fonts.googleapis.com`/`fonts.gstatic.com` present on blog.html, about.html, contact.html (sampled) |

## Current Lighthouse/PSI mobile scores (real API data, this session)

| Page | Perf | A11y | Best Practices | SEO | FCP | LCP | TBT | CLS | Speed Index |
|---|---|---|---|---|---|---|---|---|---|
| Homepage | 80 | 95 | 100 | 100 | 3.7s | 3.7s | 0ms | 0.004 | 4.6s |
| Blog post (`best-hostels-in-varanasi`) | 84 | 93 | 100 | 100 | 3.4s | 3.4s | 0ms | 0.03 | 3.7s |
| Book-now | 79 | 88 | 100 | 100 | 3.7s | 3.7s | 30ms | 0.003 | 4.9s, TTI 7.7s |

CrUX field data unavailable ("Insufficient Chrome traffic volume eligibility") — site doesn't yet have enough real-user Chrome traffic for CrUX; all above are lab (synthetic) scores only.

## New findings this pass

1. **(Medium) Redirect chain costs ~780ms on every page** — PSI's top opportunity on all 3 sampled pages is "Avoid multiple page redirects." Likely the non-www→www hop compounding with HTTP→HTTPS. Collapsing to a single redirect is a quick technical win.
2. **(Low) Book-now Time-to-Interactive is 7.7s**, notably worse than its FCP/LCP (3.7s) — a ~4s gap suggests JS execution/hydration cost from the new booking engine (Razorpay/cart) blocking interactivity after paint. Worth a JS bundle/execution audit once the new booking engine work (uncommitted, see technical.md) is deployed and re-measured.
3. **(Low) Book-now accessibility dropped to 88** (vs 93-95 elsewhere) — same contrast-ratio issue flagged sitewide plus likely form-control labeling on the booking widget; re-check after booking engine deploy.
4. Contrast-ratio audit ("Background/foreground colors do not have sufficient contrast ratio") fails on all 3 pages — sitewide, low-effort CSS fix.

## Verdict
Both baseline Critical/High performance issues are confirmed fixed. No performance regressions. Remaining gaps are new/minor (redirect chain, book-now TTI, contrast).
