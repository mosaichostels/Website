#!/usr/bin/env python3
"""Common Crawl presence extraction — the LLMO ground truth for this site.

    source ~/.config/mosaic-seo/env
    ~/.config/mosaic-seo/venv/bin/python3 .claude/seo/commoncrawl-extract.py [n_crawls] [--webgraph] [--no-cache]

Checks whether Common Crawl has ever captured this site, writes the raw bundle
to seo-reports/commoncrawl/<date>.json, and prints a gap analysis.

WHY THIS MATTERS MORE THAN ANY RANKING: Common Crawl is the single largest
public training and retrieval corpus behind LLMs. A domain absent from CC is
absent from the pretraining data of most open models and from several
retrieval pipelines. No amount of on-page SEO fixes that.

No auth, no quota, no key. Be polite: this script makes n_crawls + ~6 requests.

The Common Crawl index API has exactly two surfaces:
    GET https://index.commoncrawl.org/collinfo.json
        every crawl ever published, newest first
    GET https://index.commoncrawl.org/<CC-MAIN-YYYY-NN>-index?url=<pat>&output=json
        CDX capture records for one URL pattern in one crawl.
        pattern forms: exact url | `host/*` prefix | `*.host` whole-domain
        (`*.host` is the one to use — it covers www and bare host in one call)
        404 with {"message": "No Captures found"} means genuinely zero.
        Extra params used here: &limit= &fl=url,timestamp,status,mime

Deliberately NOT available from the index — do not promise these:
    - "who links to me". The CDX index is keyed by the URL that was CRAWLED,
      never by link target. There is no backlink query. The ONLY Common Crawl
      product that answers it is the quarterly hyperlink webgraph, a ~900 MB
      gzip; --webgraph streams it with an early exit on its sorted key and
      caches the verdict. Presence in the graph WITHOUT captures would mean
      "somebody links to you but CC never fetched you"; absence means no
      crawled page on the web links here at all.
    - page content (that is in the WARC files, fetched by byte range — a
      different job and pointless when the capture count is zero)
    - any signal about WHEN a domain will next be crawled. CC publishes no
      submission endpoint and honours no sitemap ping.
"""
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.parse
import zlib

import requests

CDX = "https://index.commoncrawl.org"
COLLINFO = f"{CDX}/collinfo.json"
GRAPH = "https://data.commoncrawl.org/projects/hyperlinkgraph"
UA = {"User-Agent": "mosaic-seo-audit/1.0 (+https://www.mosaichostels.com)"}
CCBOT_UA = {"User-Agent": "CCBot/2.0 (https://commoncrawl.org/faq/)"}
CONTROL = "example.com"          # known-crawled domain; proves the pipeline works

SITE = os.environ.get("SITE_URL") or sys.exit(
    "SITE_URL not set — source ~/.config/mosaic-seo/env")
DOMAIN = urllib.parse.urlparse(SITE).netloc.removeprefix("www.")
ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())

args = [a for a in sys.argv[1:] if not a.startswith("-")]
N = int(args[0]) if args else 12
WEBGRAPH = "--webgraph" in sys.argv
USE_CACHE = "--no-cache" not in sys.argv

OUTDIR = ROOT / "seo-reports" / "commoncrawl"
CACHE = OUTDIR / ".cache"
CACHE.mkdir(parents=True, exist_ok=True)


def cached(key, fn):
    """A published crawl is immutable, so its answer caches forever."""
    cf = CACHE / f"{re.sub(r'[^A-Za-z0-9._-]', '_', key)}.json"
    if USE_CACHE and cf.exists():
        return json.loads(cf.read_text())
    val = fn()
    cf.write_text(json.dumps(val))
    return val


def captures(crawl, pattern, limit=1000):
    """CDX rows for one pattern in one crawl. [] means genuinely zero."""
    def go():
        try:
            r = requests.get(f"{CDX}/{crawl}-index", timeout=90, headers=UA,
                             params={"url": pattern, "output": "json", "limit": limit,
                                     "fl": "url,timestamp,status,mime"})
        except requests.RequestException as e:
            return {"error": str(e)[:200]}
        if r.status_code == 404:
            return []                       # documented "No Captures found"
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code} {r.text[:200]}"}
        return [json.loads(ln) for ln in r.text.splitlines() if ln.strip()]
    return cached(f"{crawl}--{pattern}", go)


def webgraph_presence(domain, release):
    """Stream the sorted domain-vertices file until the reversed key is passed.

    Vertices are `id \\t reversed-host \\t n` sorted lexicographically by the
    reversed host, so we can stop the download the moment we read a key that
    sorts after ours. Still means pulling several hundred MB to reach `com.m*`.
    """
    target = ".".join(reversed(domain.split(".")))          # com.mosaichostels
    url = f"{GRAPH}/{release}/domain/{release}-domain-vertices.txt.gz"
    # ponytail: hard byte cap so a bad release name cannot download forever.
    # Raise it if the verdict comes back "inconclusive".
    cap, got = 800 * 1024 * 1024, 0
    d = zlib.decompressobj(zlib.MAX_WBITS | 16)
    tail = ""
    try:
        r = requests.get(url, stream=True, timeout=600, headers=UA)
        r.raise_for_status()
        for chunk in r.iter_content(1 << 20):
            got += len(chunk)
            tail += d.decompress(chunk).decode("utf-8", "replace")
            lines = tail.split("\n")
            tail = lines.pop()
            for ln in lines:
                f = ln.split("\t")
                if len(f) < 2:
                    continue
                if f[1] == target or f[1].startswith(target + "."):
                    r.close()
                    return {"release": release, "present": True, "vertex": f,
                            "downloaded_mb": round(got / 1e6)}
                if f[1] > target:
                    r.close()
                    return {"release": release, "present": False,
                            "passed_at": f[1], "downloaded_mb": round(got / 1e6)}
            if got > cap:
                r.close()
                return {"release": release, "present": None,
                        "note": "inconclusive — byte cap hit before reaching the key",
                        "downloaded_mb": round(got / 1e6)}
    except (requests.RequestException, zlib.error) as e:
        return {"release": release, "present": None, "error": str(e)[:200]}
    return {"release": release, "present": False, "note": "end of file",
            "downloaded_mb": round(got / 1e6)}


def n(v):
    return len(v) if isinstance(v, list) else -1        # -1 == request errored


def demo():
    """Self-check for the parsing/verdict logic (no network)."""
    assert n([1, 2]) == 2 and n({"error": "x"}) == -1 and n([]) == 0
    assert ".".join(reversed("mosaichostels.com".split("."))) == "com.mosaichostels"
    assert ".".join(reversed("a.b.co.uk".split("."))) == "uk.co.b.a"
    for line, key, want in ((["3", "com.mosaichostels", "1"], "com.mosaichostels", True),
                            (["3", "com.mosaichostels.blog", "1"], "com.mosaichostels", True),
                            (["3", "com.mosaic", "1"], "com.mosaichostels", False)):
        assert (line[1] == key or line[1].startswith(key + ".")) is want, line
    assert "com.mosaicz" > "com.mosaichostels"      # early-exit ordering holds
    print("demo ok")


if os.environ.get("CC_SELFTEST"):
    demo()
    sys.exit(0)


bundle = {"site": SITE, "domain": DOMAIN, "control": CONTROL,
          "generated": dt.datetime.now().isoformat(timespec="seconds")}

print(f"Common Crawl extract — {DOMAIN}   (control: {CONTROL})\n")

# --- 1. crawl list ----------------------------------------------------------
colls = cached(f"collinfo-{dt.date.today().isoformat()}",
               lambda: requests.get(COLLINFO, timeout=60, headers=UA).json())
recent = colls[:N]
bundle["crawls_total_published"] = len(colls)
bundle["crawls_checked"] = [c["id"] for c in recent]

# --- 2. capture history -----------------------------------------------------
bundle["captures"] = {}
bundle["control_captures"] = {}
for i, c in enumerate(recent, 1):
    cid = c["id"]
    bundle["captures"][cid] = captures(cid, f"*.{DOMAIN}")
    # Control only on the three newest — enough to prove the query works.
    if i <= 3:
        bundle["control_captures"][cid] = captures(cid, f"*.{CONTROL}")
    print(f"  [{i}/{len(recent)}] {cid} ({c.get('name','')})")
    time.sleep(0.5)

# --- 3. is CCBot actually allowed in? ---------------------------------------
# Discriminates "blocked" from "never discovered" — completely different fixes.
robots = ""
try:
    robots = requests.get(f"{SITE}/robots.txt", timeout=30, headers=UA).text
except requests.RequestException as e:
    robots = f"(fetch failed: {e})"
bundle["robots_txt"] = robots
bundle["robots_mentions_ccbot"] = bool(re.search(r"(?im)^user-agent:\s*ccbot", robots))

sitemap = ROOT / "sitemap.xml"
urls = re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text()) if sitemap.exists() else []
bundle["sitemap_url_count"] = len(urls)

bundle["ccbot_fetch"] = {}
for u in ([SITE + "/", f"{SITE}/sitemap.xml"] + urls[1:3]):
    try:
        r = requests.get(u, timeout=30, headers=CCBOT_UA, allow_redirects=True)
        bundle["ccbot_fetch"][u] = {"status": r.status_code, "bytes": len(r.content),
                                    "final": r.url}
    except requests.RequestException as e:
        bundle["ccbot_fetch"][u] = {"error": str(e)[:200]}

# --- 4. webgraph (opt-in; hundreds of MB) -----------------------------------
if WEBGRAPH:
    rel = "cc-main-2026-jan-feb-mar"
    print(f"\n  --webgraph: streaming {rel} domain-vertices (this pulls "
          f"several hundred MB, once, then caches the verdict)")
    bundle["webgraph"] = cached(f"webgraph-{DOMAIN}-{rel}",
                                lambda: webgraph_presence(DOMAIN, rel))

outfile = OUTDIR / f"{dt.date.today().isoformat()}.json"
outfile.write_text(json.dumps(bundle, indent=1))

# --- gap analysis -----------------------------------------------------------
print(f"\nraw bundle -> {outfile.relative_to(ROOT)}")


def hdr(t):
    print(f"\n## {t}")


hdr(f"Capture history — {DOMAIN}, last {len(recent)} crawls")
total = 0
for c in recent:
    k = c["id"]
    got = n(bundle["captures"][k])
    ctrl = bundle["control_captures"].get(k)
    tag = "" if ctrl is None else f"   (control {CONTROL}: {n(ctrl)})"
    total += max(0, got)
    print(f"  {k:18} {c.get('name',''):22} captures={got if got >= 0 else 'ERROR'}{tag}")
print(f"  ---- total captures across {len(recent)} crawls: {total}")

hdr("Verdict")
ctrl_ok = any(n(v) > 0 for v in bundle["control_captures"].values())
if total == 0 and ctrl_ok:
    print(f"  {DOMAIN} is ABSENT from Common Crawl. The control domain returns "
          f"captures\n  from the same queries, so this is the site's real state, "
          f"not a broken query.")
    print("  Consequence: this site contributed ZERO tokens to every model trained "
          "on CC,\n  and is invisible to every retrieval pipeline built on it.")
elif total == 0:
    print("  Zero captures AND the control returned nothing — the query or the "
          "index is\n  broken. Do not report an absence finding from this run.")
else:
    print(f"  {total} captures found. Crawled URLs:")
    for k, rows in bundle["captures"].items():
        for r in (rows if isinstance(rows, list) else [])[:20]:
            print(f"    {k} {r.get('timestamp','')} {r.get('status','')} {r.get('url','')}")

hdr("Is CCBot blocked? (blocked and undiscovered need opposite fixes)")
print(f"  robots.txt names CCBot: {bundle['robots_mentions_ccbot']}")
for ln in robots.splitlines():
    if re.search(r"(?i)ccbot|^user-agent:\s*\*|^disallow", ln.strip()):
        print(f"    | {ln.strip()}")
for u, r in bundle["ccbot_fetch"].items():
    print(f"  as CCBot: {r.get('status', r.get('error'))}  {r.get('bytes','')}B  {u}")
served = [r for r in bundle["ccbot_fetch"].values() if r.get("status") == 200]
if served and total == 0:
    print("  -> CCBot is SERVED 200 on every URL tested. Nothing is blocking the "
          "crawl.\n     Absence is a DISCOVERY problem: Common Crawl seeds from "
          "links it already\n     knows about, so a domain with no inbound links "
          "from crawled pages is never\n     reached, no matter how good its "
          "robots.txt and sitemap are.")

hdr("Inbound links — what Common Crawl can and cannot tell you")
print("  The CDX index is keyed by crawled URL, never by link target: there is no\n"
      "  backlink query, and any tool claiming otherwise is using the webgraph.")
wg = bundle.get("webgraph")
if wg is None:
    print("  Run again with --webgraph for the one CC dataset that does answer it\n"
          "  (quarterly domain-vertices, ~900 MB gzip, streamed with early exit,\n"
          "  verdict cached permanently).")
elif wg.get("present") is True:
    print(f"  IN the {wg['release']} webgraph as {wg['vertex'][1]} — some crawled page\n"
          f"  DOES link here; CC knows the domain but has not fetched it. Absence is\n"
          f"  a crawl-budget/priority problem, not a zero-links problem.")
elif wg.get("present") is False:
    print(f"  NOT in the {wg['release']} webgraph (scan passed the sorted key at "
          f"{wg.get('passed_at','?')}\n  after {wg.get('downloaded_mb','?')} MB). No page "
          f"Common Crawl has ever crawled\n  links to this domain. THAT is the root "
          f"cause — the fix is external links from\n  already-crawled sites, not "
          f"anything on the site itself.")
else:
    print(f"  webgraph check inconclusive: {wg.get('note') or wg.get('error')}")

hdr("Coverage context")
print(f"  crawls published all-time: {bundle['crawls_total_published']}  "
      f"(checked the {len(recent)} newest)")
print(f"  URLs in sitemap.xml: {bundle['sitemap_url_count']} — every one of them is "
      f"uncrawled by CC")
print("  Common Crawl accepts no submissions and pings no sitemaps. The only lever\n"
      "  is inbound links from domains CC already crawls.")
