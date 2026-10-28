# Agent context router (Website)

Mosaic Hostel Varanasi: static HTML site + PHP booking/payment API (eZee + Razorpay), manual FTP deploy. Live https://www.mosaichostels.com.
Verified 2026-10-29 @ fd29588. Branch `main` (2 commits ahead of `origin/main`); single worktree, the real code is this checkout.
Skip `OpenMontage/` (vendored video tool). Never read `api/secrets.php`. Pushing/deploying needs the owner's approval.

## Task -> files (always read STATUS.md)
| Task | Read |
|---|---|
| Bug fix | GOTCHAS, ARCHITECTURE, FLOWS/, TESTING |
| Booking, payment, cancel, PHP change | FLOWS/booking, FLOWS/cancellation, API, DATA, GOTCHAS, TESTING |
| Guest paid but no booking / alert mail | RUNBOOKS/paid-no-booking, FLOWS/payment-recovery, OBSERVABILITY |
| New page, blog post, copy edit | CONVENTIONS, STRUCTURE, DECISIONS, FLOWS/content-publish |
| Shared JS/CSS edit | CONVENTIONS (cache bust), COMMANDS |
| Deploy / site broken after deploy | DEPLOY, RUNBOOKS/site-incident, COMMANDS, ENVIRONMENT |
| SEO run or finding | FLOWS/weekly-seo, COMMANDS, CONVENTIONS |
| Integrations, secrets, access | INTEGRATIONS, AUTH, ENVIRONMENT, EXTERNAL |
| Onboarding / "what is this" | OVERVIEW, STACK, STRUCTURE, GLOSSARY |

## Files
| File | One line |
|---|---|
| [OVERVIEW](OVERVIEW.md) | Product, audience, rooms, policies, pages |
| [STACK](STACK.md) | Tech, hosting, services, versions |
| [STRUCTURE](STRUCTURE.md) | Directory map, git-ignored paths |
| [COMMANDS](COMMANDS.md) | Deploy, test, SEO, sync commands |
| [ARCHITECTURE](ARCHITECTURE.md) | Page loading, URL rules, caching, headers, SEO program |
| [FLOWS/](FLOWS/) | booking, cancellation, payment-recovery, content-publish, weekly-seo |
| [DATA](DATA.md) | Order folders and record keys, SEO data (no database) |
| [API](API.md) | Endpoints, auth, limits, helpers |
| [AUTH](AUTH.md) | Signatures, secrets, trust boundaries |
| [INTEGRATIONS](INTEGRATIONS.md) | eZee, Razorpay, Hostinger, analytics, SEO APIs |
| [JOBS](JOBS.md) | Cron, webhook, manual jobs |
| [DEPLOY](DEPLOY.md) | FTP release, deploy sets, rollback |
| [RUNBOOKS/](RUNBOOKS/) | paid-no-booking, site-incident |
| [CONVENTIONS](CONVENTIONS.md) | Cache bust, post checklist, copy claims, commits |
| [ENVIRONMENT](ENVIRONMENT.md) | Env/constant NAMES, tools, hooks, MCP |
| [TESTING](TESTING.md) | What to run per change, last results |
| [OBSERVABILITY](OBSERVABILITY.md) | Logs, alerts, where to look |
| [EXTERNAL](EXTERNAL.md) | Accounts, consoles, local-only notes |
| [GLOSSARY](GLOSSARY.md) | Domain and system terms |
| [DECISIONS](DECISIONS.md) | Dated decisions, open questions |
| [GOTCHAS](GOTCHAS.md) | Pitfalls, booking root cause, agent config layout |
| [STATUS](STATUS.md) | Current state, recent work, open items |

[COVERAGE.md](COVERAGE.md): 10 topics `unknown`. Full read of every doc is about 19.3k tokens (sum of `tokens_est` in `INDEX.json`); read only the table rows for your task.
Other sources: `PRODUCT.md` (owner-confirmed facts), `DESIGN.md` (tokens), `.claude/skills/*/SKILL.md`, `.planning/` (local).
After changing code, update the affected file and STATUS.md, then `python3 /Users/naveen/.agents/hooks/project_context_index.py docs/agent`.
