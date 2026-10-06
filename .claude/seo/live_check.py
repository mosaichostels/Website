#!/usr/bin/env python3
"""Post-deploy check of the LIVE site against live_check.json. Read-only; stdlib only.

    python3 .claude/seo/live_check.py            # exit 1 when anything fails

Checks: every URL in the live sitemap.xml answers 200; every URL in the "status" table
answers its expected code; every "redirects" entry answers one 301 to the expected target
and the target then resolves to 200 (so no redirect chains). Edit live_check.json when a
URL is added, removed or redirected on purpose.
"""
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).parent


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


_opener = urllib.request.build_opener(_NoRedirect)


def fetch(url):
    """(status, location, body). Redirects are NOT followed. Status 0 means a transport error."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 live-check"})
    try:
        r = _opener.open(req, timeout=25)
        return r.status, r.headers.get("location", ""), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("location", ""), ""
    except (urllib.error.URLError, OSError):  # timeout, DNS, connection reset: reported as status 0
        return 0, "", ""


def evaluate(cfg, fetch_fn):
    """Return (checked_count, failures). fetch_fn(url) -> (status, location, body)."""
    site = cfg["site"].rstrip("/")
    failures, checked = [], 0
    code, _, body = fetch_fn(site + "/sitemap.xml")
    sitemap = re.findall(r"<loc>([^<]+)</loc>", body) if code == 200 else []
    if not sitemap:
        failures.append(f"sitemap.xml unreadable (HTTP {code})")
    for url in sitemap:
        checked += 1
        got = fetch_fn(url)[0]
        if got != 200:
            failures.append(f"{url}: expected 200, got {got}")
    for want, paths in cfg["status"].items():
        for p in paths:
            checked += 1
            got = fetch_fn(site + p)[0]
            if got != int(want):
                failures.append(f"{p}: expected {want}, got {got}")
    for src, dest in cfg["redirects"]:
        checked += 1
        code, loc, _ = fetch_fn(site + src)
        want = site + dest
        if code != 301 or loc != want:
            failures.append(f"{src}: expected 301 to {want}, got {code} {loc}")
            continue
        final = fetch_fn(loc.split("#")[0])[0]
        if final != 200:
            failures.append(f"{src}: target {dest} answers {final}, not 200 (redirect chain or dead end)")
    return checked, failures


def main():
    cfg = json.loads((HERE / "live_check.json").read_text())
    checked, failures = evaluate(cfg, fetch)
    for f in failures:
        print("FAIL", f)
    print(f"checked {checked} URLs: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
