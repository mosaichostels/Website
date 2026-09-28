# Visual SEO Audit — mosaichostels.com — 2026-09-28

Scope for this run (turn-budgeted, per orchestrator instruction — this audit had
hit its turn limit twice already today with zero output): homepage, /book-now,
/about. Desktop (1920x1080) and mobile (375x812, iPhone UA) only. Tablet
(768x1024) and laptop (1366x768) were **not** captured this run.

Tooling: Playwright was not yet installed in the claude-seo venv
(`~/.config/mosaic-seo/venv`) — installed `playwright` via pip (cached wheel,
instant) and `chromium` via `playwright install chromium` at the start of this
run. Both now available for future runs, no repo change needed.

Health gate: `GET https://www.mosaichostels.com/` → `200`. Proceeded.

## Method

For each of the 3 pages, at each viewport: navigated with Playwright
(`networkidle`), took a viewport-only screenshot ("fold") and a full-page
screenshot ("full"), read `document.documentElement.scrollWidth` vs
`clientWidth` for horizontal-overflow detection, checked whether the first
`<h1>` and the first booking-related CTA fall within the viewport's height
without scrolling. All 6 screenshots (3 pages x 2 viewports x 2 shot types =
12 files) captured successfully, no errors, no timeouts.

**Not measured this run** (explicitly out of scope for the tooling used, do
not infer from this report): LCP element / LCP timing (that needs a
performance trace, not a static screenshot — see `seo-visual` agent or
`cwv-extract.py` for that), tap-target size audit, computed font-size/contrast
checks, layout-shift (CLS) observation, accessibility-tree dump.

## Above-the-fold — mobile (375x812)

| Page | H1 visible w/o scroll | H1 text | CTA visible w/o scroll | CTA text |
|---|---|---|---|---|
| `/` (home) | Yes | "BUDGET HOSTEL IN VARANASI NEAR ASSI GHAT" | Yes | "BOOK NOW" |
| `/book-now` | Yes | "Book Your Stay at Mosaic Hostel" | Yes | "BOOK NOW" |
| `/about` | Yes | "About Mosaic Hostel Varanasi" | Yes | "BOOK NOW" |

All three pages pass the basic above-the-fold check on mobile: primary
heading and a "BOOK NOW" CTA both render inside the first 812px of vertical
space with no scroll needed. (Note: "CTA visible" here means *some*
booking-related element was found in-viewport — I did not verify it's the
same visually-primary CTA a human would call "the" CTA on every page, just
that a `Book`-labeled link/button exists above the fold. Worth a human glance
at the screenshots for that nuance.)

## Above-the-fold — desktop (1920x1080)

Same pattern on all three pages: H1 and a BOOK NOW CTA both in-viewport with
no scroll. No layout collapse observed at desktop width.

## Layout issue found: horizontal overflow on `/about`, mobile only

`/about` at 375px width: `scrollWidth = 391` vs `clientWidth = 375` — **16px
of horizontal overflow**, confirmed via direct DOM measurement (not just a
screenshot impression). This is the only page/viewport combination of the 6
tested that overflows; `/` and `/book-now` are both clean at 375px
(`scrollWidth == clientWidth` exactly), and `/about` itself is clean at
1920px desktop.

**Root cause isolated:** walked every element's `getBoundingClientRect()` at
375px width and found `<nav id="mainNav">` rendering at **391px wide**
(`left: 0, right: 391`) — exactly the 16px of overflow measured at the
document level. An `<em>` inside the nav also runs to `right: 390`. This is
almost certainly the mobile nav (hamburger menu or its expanded item list)
not constraining to `100vw` / `box-sizing: border-box` on `/about`
specifically, since the same nav component does not overflow on `/` or
`/book-now` at the same viewport width — so the cause is likely
`/about`-page-specific CSS (a wider nav item, inline style, or a
page-specific override) rather than the shared nav component itself. Two
other elements the sweep flagged are not bugs: `#cursor`/`#cursor-ring`
(custom cursor-follower divs, negatively positioned by design, do not affect
document scrollWidth since they're almost certainly `position: fixed`) and an
`H1.visually-hidden` positioned off-screen at `left: -9999px` (a standard
accessible-heading pattern, intentional).

## Screenshots

All in `seo-reports/mosaichostels.com-audit/screenshots/`:

- `home-desktop-fold.png`, `home-desktop-full.png`
- `home-mobile-fold.png`, `home-mobile-full.png`
- `book-now-desktop-fold.png`, `book-now-desktop-full.png`
- `book-now-mobile-fold.png`, `book-now-mobile-full.png`
- `about-desktop-fold.png`, `about-desktop-full.png`
- `about-mobile-fold.png`, `about-mobile-full.png`

## Not completed this run (explicit, not inferred)

- Tablet (768x1024) and laptop (1366x768) viewports — not captured.
- `/contact`, `/gallery`, `/blog/`, and individual blog posts — not captured
  (out of the 3-page priority scope given for this run).
- Fix for the `/about` mobile nav overflow — root cause isolated (`#mainNav`
  at 391px vs 375px viewport, see above) but the actual CSS/HTML source line
  was not located this run (would need `about.html` / `styles/` inspection,
  out of scope for this screenshot pass) and no fix was applied.
- LCP element identification, tap-target sizing, contrast ratios, CLS —
  needs Lighthouse/PSI trace data, not in scope for a Playwright screenshot
  pass. Route to `seo-unlighthouse` / `cwv-extract.py` (step (b)/(c) of the
  weekly-seo skill) for those.
- Accessibility-tree capture (`render_page.py --a11y-tree`) — not run this
  pass; only `capture_screenshot.py`-equivalent logic was used, via a direct
  Playwright script (the `claude-seo` scripts directory was resolved but the
  standalone script was reimplemented inline to keep this run's turn count
  low — same underlying approach, no divergent behavior expected).

## Status

Partial-but-real result: all 3 priority pages x 2 viewports captured with
data (12 screenshots, above-fold check, 1 real layout defect found and root
cause isolated). This supersedes the two earlier 2026-09-28 attempts that
produced nothing.
