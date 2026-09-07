#!/usr/bin/env python3
"""Unlighthouse lab sweep + claude-seo drift comparison, in one durable bundle.

    source ~/.config/mosaic-seo/env
    ~/.config/mosaic-seo/venv/bin/python3 .claude/seo/lighthouse-drift-extract.py [--key-pages]

Runs `unlighthouse-ci` across the site, harvests every per-page Lighthouse
report before Unlighthouse throws them away, compares the key pages against
their stored claude-seo drift baselines, writes the raw bundle to
seo-reports/lighthouse/<date>.json and prints a gap analysis.

--key-pages skips the full sitemap sweep and audits only /, /book-now, /blog
(~1 min instead of ~4). --refresh-baselines re-captures drift baselines after
comparing, i.e. accepts the current state as the new known-good.

WHAT UNLIGHTHOUSE GIVES YOU
    Lighthouse 13 lab data for many URLs in one pass: the four category scores
    per page, every audit with its score, displayValue and numeric savings
    (bytes / ms), and the lab metrics (FCP, LCP, TBT, CLS, SI, TTI).
    Route discovery comes from sitemap.xml, then dynamic sampling collapses
    same-shaped routes — this site's 23 sitemap URLs audit as 15 routes, the
    blog posts sampled. Pass --disable-dynamic-sampling to audit every one.

WHAT IT CANNOT GIVE YOU — do not present these as measurements:
    - Field data. Every number here is a simulated-throttle lab run on this
      laptop, from this network. Real-user LCP/INP/CLS comes from CrUX
      (`claude-seo run crux_history.py`) or the PSI API, never from here.
    - Stable performance scores. The performance category swings +/-10 between
      runs on identical HTML; treat a single run's perf number as a range.
      SEO / accessibility / best-practices are deterministic and comparable.
    - INP. Lighthouse lab reports TBT as its proxy; INP needs real interaction.
    - Anything behind the CDN edge (origin TTFB, cache-hit ratio).
    - A per-page HTML report, unless --build-static is passed — and that flag
      is exactly what deletes the per-page lighthouse.json files afterwards
      (@unlighthouse/cli ci.mjs, buildStatic branch). This script never passes
      it, and copies the audit detail into the bundle before the temp output
      dir is removed, so the detail survives the run either way.

WHAT THE claude-seo DRIFT SYSTEM GIVES YOU
    A SQLite snapshot per URL (title, meta description, canonical, robots,
    H1/H2s, JSON-LD, OG/Twitter tags, status code, content hash) and 17
    comparison rules over it, graded CRITICAL / WARNING / INFO. It answers
    "did a deploy silently break the head of this page".

WHAT IT CANNOT GIVE YOU:
    - Anything about pages you never baselined. It is a diff, not a crawler.
    - Rankings, traffic or index state — that is gsc-extract.py.
    - Rendered-DOM checks: it reads raw HTML, so JS-injected tags look missing.
    - Any history if the baseline DB is lost. The plugin hardcodes
      ~/.cache/claude-seo/drift/, which is a cache path a cleanup will wipe;
      here it is a symlink to ~/.local/share/mosaic-seo/drift. This script
      refuses to continue if that symlink has been replaced by a real dir.
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import re
import shutil
import subprocess
import sqlite3
import sys
import tempfile

SITE = os.environ.get("SITE_URL") or sys.exit("SITE_URL not set — source ~/.config/mosaic-seo/env")
KEY_PAGES = ["/", "/book-now", "/blog/"]
SWEEP_TIMEOUT = 1800

ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())
CACHE_LINK = pathlib.Path("~/.cache/claude-seo/drift").expanduser()
SAFE_STORE = pathlib.Path("~/.local/share/mosaic-seo/drift").expanduser()

ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
ap.add_argument("--key-pages", action="store_true", help="audit only / /book-now /blog")
ap.add_argument("--skip-sweep", action="store_true", help="drift only, no Lighthouse")
ap.add_argument("--skip-drift", action="store_true", help="Lighthouse only")
ap.add_argument("--refresh-baselines", action="store_true",
                help="re-capture drift baselines after comparing (accept current state)")
ap.add_argument("--self-check", action="store_true", help="run assertions and exit")
args = ap.parse_args()

if args.self_check:
    import re as _re
    _kib = lambda d: (lambda m: m and round(float(m.group(1)) * {"KiB": 1024, "MiB": 1048576, "bytes": 1}[m.group(2)]))(_re.search(r"([\d.]+)\s*(KiB|MiB|bytes)", d or ""))
    assert _kib("Est savings of 97 KiB") == 99328, _kib("Est savings of 97 KiB")
    assert _kib("Est savings of 1.5 MiB") == 1572864
    assert _kib("8 cookies found") is None and _kib(None) is None
    assert CACHE_LINK.is_symlink() and CACHE_LINK.resolve() == SAFE_STORE.resolve(), \
        "drift baselines are not on the durable path"
    print("self-check OK")
    sys.exit(0)

bundle = {"site": SITE, "mode": "key-pages" if args.key_pages else "full-sweep",
          "generated": dt.datetime.now().isoformat(timespec="seconds")}

print(f"Lighthouse + drift extract — {SITE}   mode={bundle['mode']}\n")


# --- 1. Unlighthouse sweep --------------------------------------------------
def kib(display_value):
    """Recover the byte figure from 'Est savings of 97 KiB' — LH13 insight
    audits print it and no longer expose it as a field."""
    m = re.search(r"([\d.]+)\s*(KiB|MiB|bytes)", display_value or "")
    if not m:
        return None
    return round(float(m.group(1)) * {"KiB": 1024, "MiB": 1048576, "bytes": 1}[m.group(2)])


def sweep():
    """Run unlighthouse-ci into a temp dir, harvest the per-page LHRs, bin the dir."""
    out = tempfile.mkdtemp(prefix="unlighthouse-")
    cmd = ["unlighthouse-ci", "--site", SITE, "--output-path", out,
           "--reporter", "jsonExpanded", "--no-cache"]
    if args.key_pages:
        cmd += ["--urls", ",".join(KEY_PAGES)]
    print(f"  $ {' '.join(cmd[:4])} ...  (several minutes, do not interrupt)")
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=SWEEP_TIMEOUT)
        # unlighthouse-ci exits 1 when a score budget fails; we set no budget,
        # so a non-zero exit alongside a written ci-result.json is still usable.
        ci = pathlib.Path(out) / "ci-result.json"
        result = {"exit_code": p.returncode}
        if not ci.exists():
            result["error"] = (p.stderr or p.stdout)[-2000:]
            return result
        result.update(json.loads(ci.read_text()))

        # Per-page detail. Unlighthouse keeps a full lighthouse.json per route
        # under the output dir; nothing else exposes the audit-level savings.
        result["audits"] = {}
        for lhr_path in sorted(pathlib.Path(out).rglob("lighthouse.json")):
            try:
                lhr = json.loads(lhr_path.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            url = lhr.get("finalDisplayedUrl") or lhr.get("requestedUrl") or str(lhr_path)
            result.setdefault("lighthouse_version", lhr.get("lighthouseVersion"))
            # The scored metric audits (LCP, TTI, SI...) are reported in the
            # metrics block already; leaving them in the audit list buries the
            # dozen audits you can actually act on.
            metric_ids = {ref["id"] for cat in (lhr.get("categories") or {}).values()
                          for ref in cat.get("auditRefs", [])
                          if ref.get("group") in ("metrics", "hidden")}
            failing = {}
            for aid, a in (lhr.get("audits") or {}).items():
                score = a.get("score")
                if score is None or score >= 1 or aid in metric_ids:
                    continue          # passing, informative, notApplicable or a metric
                det = a.get("details") or {}
                msav = a.get("metricSavings") or {}
                failing[aid] = {
                    "title": a.get("title"),
                    "score": score,
                    "displayValue": a.get("displayValue"),
                    # Lighthouse 13 dropped overallSavings* from the new
                    # *-insight audits and only reports per-metric ms there,
                    # with the byte figure left in the displayValue string.
                    "savings_ms": det.get("overallSavingsMs")
                                  or max([v for v in msav.values() if v] or [0]) or None,
                    "savings_bytes": det.get("overallSavingsBytes") or kib(a.get("displayValue")),
                    "metric_savings": msav,
                    "items": len(det.get("items") or []),
                }
            result["audits"][url] = failing
        return result
    except subprocess.TimeoutExpired:
        return {"error": f"unlighthouse-ci exceeded {SWEEP_TIMEOUT}s"}
    finally:
        shutil.rmtree(out, ignore_errors=True)


bundle["unlighthouse"] = {} if args.skip_sweep else sweep()


# --- 2. claude-seo drift ----------------------------------------------------
def drift():
    """Verify the baseline store, then compare (or capture) each key page."""
    d = {"store": {}}
    d["store"]["cache_path_is_symlink"] = CACHE_LINK.is_symlink()
    d["store"]["resolves_to"] = str(CACHE_LINK.resolve())
    d["store"]["safe"] = CACHE_LINK.is_symlink() and CACHE_LINK.resolve() == SAFE_STORE.resolve()
    if not d["store"]["safe"]:
        d["error"] = (f"{CACHE_LINK} is not a symlink to {SAFE_STORE}. Baselines are "
                      f"sitting in a cache dir and a cleanup will destroy them. Fix:\n"
                      f"  mkdir -p {SAFE_STORE} && mv {CACHE_LINK}/* {SAFE_STORE}/ 2>/dev/null;\n"
                      f"  rmdir {CACHE_LINK} && ln -s {SAFE_STORE} {CACHE_LINK}")
        return d

    scripts = sorted(pathlib.Path("~/.claude/plugins/cache").expanduser().glob(
        "*/claude-seo/*/scripts"))
    if not scripts:
        d["error"] = "claude-seo plugin scripts not found"
        return d
    sys.path.insert(0, str(scripts[-1]))
    from drift_baseline import DB_PATH, capture_baseline      # noqa: E402
    from drift_compare import run_comparison                  # noqa: E402

    with sqlite3.connect(DB_PATH) as conn:
        d["store"]["baselines"] = [
            {"id": r[0], "url": r[1], "captured": r[2]}
            for r in conn.execute("SELECT id, url, timestamp FROM baselines ORDER BY id")]
    known = {b["url"] for b in d["store"]["baselines"]}

    d["pages"] = {}
    for path in KEY_PAGES:
        url = SITE.rstrip("/") + path
        try:
            if url.rstrip("/") in known or url in known:
                d["pages"][path] = run_comparison(url, skip_cwv=True)
                if args.refresh_baselines:
                    d["pages"][path]["refreshed"] = capture_baseline(url, skip_cwv=True).get("baseline_id")
            else:
                d["pages"][path] = {"status": "captured",
                                    **capture_baseline(url, skip_cwv=True)}
        except Exception as e:                                # noqa: BLE001
            d["pages"][path] = {"error": f"{type(e).__name__}: {e}"[:300]}
    return d


bundle["drift"] = {} if args.skip_drift else drift()


# --- persist ----------------------------------------------------------------
outdir = ROOT / "seo-reports" / "lighthouse"
outdir.mkdir(parents=True, exist_ok=True)
outfile = outdir / f"{dt.date.today().isoformat()}.json"
outfile.write_text(json.dumps(bundle, indent=1))
print(f"\nraw bundle -> {outfile.relative_to(ROOT)}")


# --- gap analysis -----------------------------------------------------------
def hdr(t):
    print(f"\n## {t}")


ul = bundle["unlighthouse"]
CATS = ["performance", "accessibility", "best-practices", "seo"]

if ul.get("error"):
    hdr("Unlighthouse")
    print(f"  FAILED: {ul['error'][:500]}")
elif ul:
    routes = ul.get("routes", [])
    hdr(f"Per-page category scores ({len(routes)} routes, Lighthouse "
        f"{ul.get('lighthouse_version', '?')})")
    print(f"  {'route':40} {'perf':>5} {'a11y':>5} {'bestp':>5} {'seo':>5}")
    for r in routes:
        c = r.get("categories", {})
        print(f"  {r['path'][:40]:40} " +
              " ".join(f"{round((c.get(k, {}).get('score') or 0) * 100):5}" for k in CATS))
    avg = ul.get("summary", {}).get("categories", {})
    print(f"  {'AVERAGE':40} " +
          " ".join(f"{round((avg.get(k, {}).get('averageScore') or 0) * 100):5}" for k in CATS))
    for k in CATS:
        scores = [round((r.get("categories", {}).get(k, {}).get("score") or 0) * 100)
                  for r in routes]
        if scores:
            worst = min(routes, key=lambda r: r.get("categories", {}).get(k, {}).get("score") or 0)
            print(f"  {k:16} min={min(scores):3} on {worst['path']}")

    hdr("Lab metrics (site average — lab, not field; do not quote as CWV)")
    for mid, m in sorted((ul.get("summary", {}).get("metrics") or {}).items()):
        print(f"  {mid:36} {m.get('averageNumericValue')}")

    # Roll the per-page failures up: one row per audit, how many pages it hits,
    # and the total savings on offer. That ordering is the fix queue.
    audits = ul.get("audits", {})
    n_pages = len(audits)
    index = {}
    for url, fails in audits.items():
        for aid, a in fails.items():
            e = index.setdefault(aid, {"title": a["title"], "pages": [], "ms": 0, "bytes": 0})
            e["pages"].append(url)
            e["ms"] += a.get("savings_ms") or 0
            e["bytes"] += a.get("savings_bytes") or 0
    bundle["audit_index"] = index

    hdr(f"Failing audits by reach ({n_pages} pages audited)")
    print(f"  {'pages':>5}  {'save ms':>8} {'save KiB':>9}  audit")
    for aid, e in sorted(index.items(), key=lambda x: (-len(x[1]["pages"]), -x[1]["ms"])):
        print(f"  {len(e['pages']):3}/{n_pages:<2}  {round(e['ms']):8} {round(e['bytes']/1024):9}  "
              f"{aid} — {e['title'][:60]}")

    hdr("Biggest single-page wins")
    flat = [(url, aid, a) for url, fails in audits.items() for aid, a in fails.items()
            if (a.get("savings_ms") or 0) > 0 or (a.get("savings_bytes") or 0) > 0]
    for url, aid, a in sorted(flat, key=lambda x: (-(x[2].get("savings_ms") or 0),
                                                   -(x[2].get("savings_bytes") or 0)))[:12]:
        print(f"  {round(a.get('savings_ms') or 0):6}ms {round((a.get('savings_bytes') or 0)/1024):6}KiB  "
              f"{aid:34} {url.replace(SITE, '') or '/'}")

    hdr("Site-wide failures (every audited page)")
    universal = [aid for aid, e in index.items() if len(e["pages"]) == n_pages]
    for aid in sorted(universal):
        print(f"  {aid} — {index[aid]['title'][:80]}")
    if not universal:
        print("  none")

dr = bundle["drift"]
if dr.get("error"):
    hdr("Drift baseline store")
    print(f"  {dr['error']}")
elif dr:
    hdr("Drift baseline store")
    s = dr["store"]
    print(f"  ~/.cache/claude-seo/drift -> {s['resolves_to']}  "
          f"{'OK (survives a cache wipe)' if s['safe'] else 'AT RISK'}")
    for b in s["baselines"]:
        print(f"  #{b['id']}  {b['captured'][:19]}  {b['url']}")

    hdr("Drift findings vs baseline")
    for path, res in dr["pages"].items():
        if res.get("error"):
            print(f"  {path:14} ERROR {res['error']}")
        elif res.get("status") == "captured":
            print(f"  {path:14} no baseline existed — captured #{res.get('baseline_id')}")
        else:
            sm = res.get("summary", {})
            flag = "CLEAN" if not sm.get("triggered") else \
                f"{sm.get('critical',0)}C {sm.get('warning',0)}W {sm.get('info',0)}I"
            print(f"  {path:14} vs baseline #{res.get('baseline_id')} "
                  f"({res.get('baseline_timestamp','?')[:10]})  {flag}")
            for f in res.get("triggered_findings", []):
                print(f"      [{f['severity']:8}] {f['rule']}: {f['message'][:110]}")
            if res.get("refreshed"):
                print(f"      baseline refreshed -> #{res['refreshed']}")

# Re-write with audit_index folded in.
outfile.write_text(json.dumps(bundle, indent=1))
