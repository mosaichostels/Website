#!/usr/bin/env python3
"""GET-only synthetic check of the public booking page and availability API."""
import datetime as dt
import json
import pathlib
import subprocess
import sys
import time
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())
REPORTS = ROOT / "seo-reports"
SITE = "https://www.mosaichostels.com"


def probe(site, date, opener=urlopen):
    site = site.rstrip("/")
    today = dt.date.fromisoformat(date)
    arrival = today + dt.timedelta(days=1)
    departure = arrival + dt.timedelta(days=1)
    query = urlencode({"check_in": arrival.isoformat(), "check_out": departure.isoformat(),
                       "adults": 1, "children": 0, "rooms": 1})
    targets = (("booking", f"{site}/book-now"),
               ("availability", f"{site}/api/availability.php?{query}"))
    metrics = {"booking_status": None, "booking_latency_ms": None,
               "availability_status": None, "availability_latency_ms": None}
    errors = []
    for name, url in targets:
        start = time.monotonic()
        try:
            request = Request(url, headers={"User-Agent": "mosaic-seo-booking-probe/1.0"}, method="GET")
            with opener(request, timeout=30) as response:
                body = response.read(65537)
                status = response.status
                metrics[f"{name}_status"] = status
                metrics[f"{name}_latency_ms"] = round((time.monotonic() - start) * 1000)
                if response.geturl().split("?", 1)[0].startswith(f"{site}/api/") and name == "booking":
                    errors.append("booking page redirected into API")
                if status != 200:
                    errors.append(f"{name}: HTTP {status}")
                elif name == "availability":
                    try:
                        payload = json.loads(body) if len(body) <= 65536 else None
                    except ValueError:
                        payload = None
                    if not isinstance(payload, dict) or not isinstance(payload.get("rooms"), list):
                        errors.append("availability: response has no rooms array")
        except HTTPError as exc:
            metrics[f"{name}_status"] = exc.code
            metrics[f"{name}_latency_ms"] = round((time.monotonic() - start) * 1000)
            errors.append(f"{name}: HTTP {exc.code}")
            exc.close()
        except Exception as exc:
            errors.append(f"{name}: {type(exc).__name__}")
    return {"source": "booking-probe",
            "window": {"start": date, "end": date, "days": 1},
            "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "metrics": metrics, "findings": [], "errors": errors}


def run(date, reports=REPORTS, opener=urlopen, site=SITE):
    doc = probe(site, date, opener)
    out = pathlib.Path(reports) / "data" / date / "booking-probe.metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    return doc


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    result = run(day)
    print(json.dumps({"metrics": result["metrics"], "errors": result["errors"]}, indent=2))
    sys.exit(1 if result["errors"] else 0)
