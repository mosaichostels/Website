# Agent context router (Website)

Verified: 2026-10-23 @ 7118c3f. Live site https://www.mosaichostels.com (Mosaic Hostel Varanasi). Repo: github.com/mosaichostels/Website, branch `main`, 591 commits. Single worktree (`git worktree list`): the real code is this checkout.
Skip `OpenMontage/` (vendored video tool, excluded via `.git/info/exclude`). Never read `api/secrets.php`.

## Task -> files (read STATUS.md for every task)
| Task | Read |
|---|---|
| Bug fix | GOTCHAS, ARCHITECTURE, TESTING |
| New page or blog post | CONVENTIONS, STRUCTURE, DECISIONS |
| Edit shared JS/CSS | CONVENTIONS (cache bust), COMMANDS |
| Booking/payment/PHP change | ARCHITECTURE, GOTCHAS, TESTING, ENVIRONMENT |
| Deploy | COMMANDS, ENVIRONMENT, GOTCHAS |
| SEO run or finding | ARCHITECTURE (SEO program), COMMANDS, CONVENTIONS |
| Copy or claims edit | CONVENTIONS, DECISIONS |
| Onboarding / "what is this" | OVERVIEW, STACK, STRUCTURE |

## Files
| File | One line |
|---|---|
| [OVERVIEW.md](OVERVIEW.md) | Product, audience, rooms, success metric, repo facts |
| [STACK.md](STACK.md) | Tech, hosting, third-party services, versions seen |
| [STRUCTURE.md](STRUCTURE.md) | Directory map, file roles, git-ignored paths |
| [COMMANDS.md](COMMANDS.md) | Exact deploy, test, SEO, sync commands |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Page loading, booking/payment chain, order state dirs, caching, redirects, SEO program |
| [CONVENTIONS.md](CONVENTIONS.md) | Rules: cache bust, blog post checklist, copy claims, commits |
| [ENVIRONMENT.md](ENVIRONMENT.md) | Env var and constant NAMES, local tooling, hooks |
| [TESTING.md](TESTING.md) | What to run per change type, last results |
| [DECISIONS.md](DECISIONS.md) | Dated decisions and open questions |
| [GOTCHAS.md](GOTCHAS.md) | Pitfalls, guardrails, agent-config layout |
| [STATUS.md](STATUS.md) | Current state, recent work, open items |

## Other sources
`PRODUCT.md` (owner-confirmed product facts), `DESIGN.md` (tokens), `README.md` (older, partly stale), `.claude/skills/*/SKILL.md`, `.planning/` (git-ignored, local only).
After changing code, update the affected file here and STATUS.md.
