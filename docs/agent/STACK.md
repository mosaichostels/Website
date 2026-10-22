# Stack

- Static HTML, CSS, vanilla JS (`components/*.js`, `styles/`), no build step. Apache (`.htaccess`) on Hostinger.
- PHP endpoints in `api/` for booking and payment: eZee PMS availability/booking, Razorpay orders, verification, webhook, reconcile cron (every 5 minutes on Hostinger).
- Fonts: Cinzel, Cormorant Garamond, Jost. Palette: cream, gold, parchment plus jewel tiles (see `DESIGN.md`).
- SEO/analytics tooling: Search Console, GA4, Bing Webmaster, Microsoft Clarity, GBP, PageSpeed, IndexNow; scripts in `scripts/` and `.claude/skills/weekly-seo`. Python venv at `~/.config/mosaic-seo/venv`.
- `OpenMontage/` (untracked) is a video production tool checkout, not part of the site.
