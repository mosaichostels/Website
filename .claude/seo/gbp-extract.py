#!/usr/bin/env python3
"""Google Business Profile extraction (local discovery signals, read-only).

    source ~/.config/mosaic-seo/env
    ~/.config/mosaic-seo/venv/bin/python3 .claude/seo/gbp-extract.py [days]

Writes the raw bundle to seo-reports/gbp/<date>.json and prints a gap analysis.
GET requests only: it never replies to a review or edits the profile.

Credentials: an authorized-user OAuth file (client_id, client_secret,
refresh_token; scope business.manage). Path from GBP_CREDENTIALS_FILE, else
~/.config/gcloud/application_default_credentials.json. Values are never printed.
Account and location are discovered; GBP_ACCOUNT_ID / GBP_LOCATION_ID override.

APIs used (all read): Account Management v1, Business Information v1,
Verifications v1 (Voice of Merchant), Place Actions v1, My Business v4 (reviews;
the only current review surface), Business Profile Performance v1.

What it cannot give you: review text sentiment, photo counts, posts, Q&A, geo-grid
rank, the profile description of a LODGING listing (not exposed when empty).
Performance data lags about 3 days and the daily range is capped at 18 months.
"""
import collections
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import time

import requests

HOME = pathlib.Path.home()
CRED = pathlib.Path(os.environ.get("GBP_CREDENTIALS_FILE") or HOME / ".config/gcloud/application_default_credentials.json")
BASE = {
    "accounts": "https://mybusinessaccountmanagement.googleapis.com/v1",
    "info": "https://mybusinessbusinessinformation.googleapis.com/v1",
    "verif": "https://mybusinessverifications.googleapis.com/v1",
    "actions": "https://mybusinessplaceactions.googleapis.com/v1",
    "perf": "https://businessprofileperformance.googleapis.com/v1",
    "v4": "https://mybusiness.googleapis.com/v4",
}
DAILY = ["BUSINESS_IMPRESSIONS_DESKTOP_MAPS", "BUSINESS_IMPRESSIONS_DESKTOP_SEARCH",
         "BUSINESS_IMPRESSIONS_MOBILE_MAPS", "BUSINESS_IMPRESSIONS_MOBILE_SEARCH",
         "CALL_CLICKS", "WEBSITE_CLICKS", "BUSINESS_DIRECTION_REQUESTS", "BUSINESS_BOOKINGS"]
READ_MASK = ("name,title,storefrontAddress,phoneNumbers,websiteUri,categories,regularHours,specialHours,"
             "profile,serviceItems,openInfo,latlng,metadata")
SITE_PHONE_DIGITS = "919125492225"  # NAP phone on the site; the WhatsApp link must match it
ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip())
OUT = ROOT / "seo-reports" / "gbp"
errors = []
_token = {"v": None}


def token():
    if _token["v"]:
        return _token["v"]
    try:
        c = json.loads(CRED.read_text())
        r = requests.post("https://oauth2.googleapis.com/token", timeout=30, data={
            "client_id": c["client_id"], "client_secret": c["client_secret"],
            "refresh_token": c["refresh_token"], "grant_type": "refresh_token"})
        r.raise_for_status()
        _token["v"] = r.json()["access_token"]
    except Exception as e:  # never echo the response: it can contain account detail
        sys.exit(f"GBP auth failed ({type(e).__name__}); check {CRED} and the business.manage scope")
    return _token["v"]


def get(label, base, path, params=None):
    """GET with one retry on 429/5xx. Returns parsed JSON or None; records the error."""
    for attempt in (1, 2):
        r = requests.get(BASE[base] + path, params=params, timeout=60,
                         headers={"Authorization": f"Bearer {token()}"})
        if r.status_code in (429, 500, 502, 503) and attempt == 1:
            time.sleep(3)
            continue
        break
    if r.status_code != 200:
        errors.append(f"{label}: HTTP {r.status_code} {r.text[:120].strip()!r}")
        return None
    return r.json()


def pages(label, base, path, key, params, limit=400):
    out, tok = [], None
    while len(out) < limit:
        d = get(label, base, path, {**params, **({"pageToken": tok} if tok else {})})
        if not d:
            break
        out += d.get(key, [])
        tok = d.get("nextPageToken")
        if not tok:
            return out, d
    return out, d if d else {}


def ymd(d):
    return {"year": d.year, "month": d.month, "day": d.day}


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    today = dt.date.today()
    end = today - dt.timedelta(days=3)  # performance data lags about 3 days
    start = end - dt.timedelta(days=min(days, 540) - 1)

    acct = os.environ.get("GBP_ACCOUNT_ID")
    loc = os.environ.get("GBP_LOCATION_ID")
    if not acct:
        accts = (get("accounts", "accounts", "/accounts") or {}).get("accounts", [])
        acct = accts[0]["name"].split("/")[-1] if accts else sys.exit("no GBP account visible to these credentials")
    if not loc:
        locs = (get("locations", "info", f"/accounts/{acct}/locations", {"readMask": "name,title", "pageSize": 100}) or {}).get("locations", [])
        loc = locs[0]["name"].split("/")[-1] if locs else sys.exit("no GBP location under the account")
    print(f"GBP extract — account {acct}, location {loc}, {start} .. {end}\n")

    b = {"generated": dt.datetime.now().isoformat(timespec="seconds"), "account": acct, "location_id": loc,
         "start": start.isoformat(), "end": end.isoformat()}
    b["location"] = get("location", "info", f"/locations/{loc}", {"readMask": READ_MASK})
    b["attributes"] = get("attributes", "info", f"/locations/{loc}/attributes")
    b["voice_of_merchant"] = get("voice_of_merchant", "verif", f"/locations/{loc}/VoiceOfMerchantState")
    b["place_action_links"] = (get("place_action_links", "actions", f"/locations/{loc}/placeActionLinks") or {}).get("placeActionLinks", [])
    rv, last = pages("reviews", "v4", f"/accounts/{acct}/locations/{loc}/reviews", "reviews",
                     {"pageSize": 50, "orderBy": "updateTime desc"})
    b["reviews"] = rv
    b["review_summary"] = {"averageRating": last.get("averageRating"), "totalReviewCount": last.get("totalReviewCount")}

    ts = get("daily_metrics", "perf", f"/locations/{loc}:fetchMultiDailyMetricsTimeSeries", {
        "dailyMetrics": DAILY,
        **{f"dailyRange.startDate.{k}": v for k, v in ymd(start).items()},
        **{f"dailyRange.endDate.{k}": v for k, v in ymd(end).items()}}) or {}
    daily = []
    for grp in ts.get("multiDailyMetricTimeSeries", []):
        for s in grp.get("dailyMetricTimeSeries", []):
            for p in (s.get("timeSeries") or {}).get("datedValues", []):
                d = p["date"]
                daily.append({"date": f"{d['year']}-{d['month']:02d}-{d['day']:02d}",
                              "metric": s["dailyMetric"], "value": int(p.get("value", 0) or 0)})
    b["daily"] = daily

    m0 = (end.replace(day=1) - dt.timedelta(days=62)).replace(day=1)
    kw, _ = pages("keywords", "perf", f"/locations/{loc}/searchkeywords/impressions/monthly", "searchKeywordsCounts", {
        "monthlyRange.startMonth.year": m0.year, "monthlyRange.startMonth.month": m0.month,
        "monthlyRange.endMonth.year": end.year, "monthlyRange.endMonth.month": end.month, "pageSize": 100}, limit=300)
    b["keywords"] = kw
    b["errors"] = errors

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{today.isoformat()}.json"
    path.write_text(json.dumps(b, indent=1))
    print(f"raw bundle -> {path.relative_to(ROOT)}\n")
    report(b)
    return 1 if errors and not b["location"] else 0


def report(b):
    L = b["location"] or {}
    rv = b["reviews"]
    tot = collections.Counter()
    for r in b["daily"]:
        tot[r["metric"]] += r["value"]
    print("## Profile")
    print(f"  {L.get('title')}  open={((L.get('openInfo') or {}).get('status'))}  "
          f"voice_of_merchant={(b['voice_of_merchant'] or {}).get('hasVoiceOfMerchant')}")
    cats = L.get("categories") or {}
    print(f"  categories: {(cats.get('primaryCategory') or {}).get('displayName')} + "
          f"{[c.get('displayName') for c in cats.get('additionalCategories', [])]}")
    print("\n## Reviews")
    s = b["review_summary"]
    stars = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}
    un = [r for r in rv if not r.get("reviewReply")]
    print(f"  Google rating {s['averageRating']} from {s['totalReviewCount']} reviews; fetched {len(rv)}; unanswered {len(un)}")
    for r in un[:15]:
        print(f"    - {stars.get(r.get('starRating'), '?')}★ {r['reviewer'].get('displayName')} ({r['createTime'][:10]}): {(r.get('comment') or '')[:70]!r}")
    low = [r for r in rv if stars.get(r.get("starRating"), 5) <= 3 and r["createTime"][:7] >= (dt.date.today() - dt.timedelta(days=120)).isoformat()[:7]]
    if low:
        print(f"  low ratings (<=3★) in the last ~4 months: {len(low)}")
    print("\n## Performance (window)")
    imp = sum(v for k, v in tot.items() if k.startswith("BUSINESS_IMPRESSIONS"))
    print(f"  impressions {imp} | website clicks {tot['WEBSITE_CLICKS']} | calls {tot['CALL_CLICKS']} | "
          f"directions {tot['BUSINESS_DIRECTION_REQUESTS']} | bookings {tot['BUSINESS_BOOKINGS']}")
    acts = tot["WEBSITE_CLICKS"] + tot["CALL_CLICKS"] + tot["BUSINESS_DIRECTION_REQUESTS"]
    if acts:
        print(f"  website clicks are {100 * tot['WEBSITE_CLICKS'] / acts:.0f}% of profile actions: most local discovery never reaches the site")
    agg = collections.Counter()
    for k in b["keywords"]:
        v = k.get("insightsValue") or {}
        agg[k["searchKeyword"]] += int(v.get("value") or v.get("threshold") or 0)
    print("  top keywords:", "; ".join(f"{k} {v}" for k, v in agg.most_common(8)))
    print("\n## Profile gaps")
    gaps = []
    if not (L.get("profile") or {}).get("description"):
        gaps.append("no business description (lodging listings may not allow editing it through the API)")
    priced = [i for i in L.get("serviceItems", []) if i.get("price")]
    if priced:
        gaps.append(f"{len(priced)} service item(s) show a price (owner rule: no prices on public surfaces)")
    attrs = {a["name"]: a for a in (b["attributes"] or {}).get("attributes", [])}
    wa = [u.get("uri", "") for u in (attrs.get("attributes/url_whatsapp") or {}).get("uriValues", [])]
    if wa and SITE_PHONE_DIGITS not in re.sub(r"\D", "", wa[0]):
        gaps.append(f"WhatsApp link {wa[0]} does not match the site number {SITE_PHONE_DIGITS}")
    if len(attrs) < 6:
        gaps.append(f"only {len(attrs)} attributes set (no amenity, language or check-in attributes)")
    if not b["place_action_links"]:
        gaps.append("no place action link (no Book button)")
    if un:
        gaps.append(f"{len(un)} review(s) without an owner reply")
    print("\n".join(f"  - {g}" for g in gaps) or "  none found")
    if errors:
        print("\n## Errors (call failed; do not read the matching section as zero)")
        print("\n".join(f"  - {e}" for e in errors))


if __name__ == "__main__":
    sys.exit(main())
