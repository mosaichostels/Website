# MCP health

> Facts about the world: overwrite when re-verified.

- The uv-based MCPs (`mosaic-bing`, `mosaic-ga4`, `mosaic-gsc`) run from `~/.cache/uv/archive-v0/...`. A uv cache clean while they run deletes their environments and breaks them with `No module named 'httpcore'` (Bing) or `cannot import name '_plugin_wrapping' from 'grpc'` (GA4). Fix: relaunch each once so uv rebuilds the environment (run the launcher in `~/.config/mosaic-seo/mcp/` with stdin closed), then `/mcp` reconnect. If it recurs, find what runs the cache clean.
- `mosaic-ga4`: the Data API and (since the owner enabled `analyticsadmin.googleapis.com` on 2026-10-07) the Admin-API reads all work: property details (currency USD, industry unspecified, created 2025-10-02), annotations (one system annotation only), custom definitions, Google Ads links (none). If the Admin tools ever return `SERVICE_DISABLED` again, the API was switched off in Google Cloud project 172681397132.
- `mosaic-gsc` returns an authentication error (no OAuth, no credentials path configured); use the service-account scripts (`gsc-extract.py`, `gsc-sitemap-submit.py`) instead.
- `mosaic-gbp`: see `gbp.md` (reply endpoint patched; reconnect to load it).
- `mosaic-clarity` was not exercised this run; the Clarity extractor is unaffected.
