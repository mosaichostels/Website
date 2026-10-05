#!/usr/bin/env python3
"""Read Hostinger cron state and public CDN cache age without changing settings."""
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys
from urllib.request import Request, urlopen

ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())
REPORTS = ROOT / "seo-reports"
API = "https://developers.hostinger.com/api/hosting/v1/accounts"
SITE = "https://www.mosaichostels.com"


def check(date, token, username, opener=urlopen):
    metrics = {"cron_configured": None, "cron_interval_minutes": None,
               "cron_last_output_empty": None, "sitemap_cache_age_seconds": None,
               "llms_cache_age_seconds": None, "access_log_bot_requests": None,
               "access_log_404": None, "access_log_429": None}
    errors = []
    if token and username:
        base = f"{API}/{username}/cron-jobs"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json",
                   "User-Agent": "mosaic-seo/1.0"}
        try:
            with opener(Request(base, headers=headers, method="GET"), timeout=20) as response:
                payload = json.loads(response.read())
            jobs = payload.get("data", []) if isinstance(payload, dict) else payload
            if not isinstance(jobs, list):
                raise ValueError("cron list is not an array")
            matched = [job for job in jobs if "reconcile-pending.php" in job.get("command", "")]
            metrics["cron_configured"] = 1 if matched else 0
            if matched:
                schedule = matched[0].get("time", "")
                if schedule.startswith("*/"):
                    try:
                        metrics["cron_interval_minutes"] = int(schedule.split()[0][2:])
                    except ValueError:
                        pass
                uid = matched[0].get("uid")
                if uid:
                    with opener(Request(f"{base}/{uid}/output", headers=headers, method="GET"), timeout=20) as response:
                        output = json.loads(response.read())
                    if isinstance(output, dict):
                        metrics["cron_last_output_empty"] = 1 if not output.get("output") else 0
        except Exception as exc:
            errors.append(f"Hostinger cron: {type(exc).__name__}")
    else:
        errors.append("Hostinger API token or username missing; cron not measured")

    for name, path in (("sitemap", "/sitemap.xml"), ("llms", "/llms.txt")):
        try:
            with opener(Request(SITE + path, method="HEAD"), timeout=20) as response:
                age = response.headers.get("Age")
                if age is not None:
                    metrics[f"{name}_cache_age_seconds"] = int(age)
        except Exception as exc:
            errors.append(f"{name} cache age: {type(exc).__name__}")
    errors.append("Hostinger access-log bot/404/429 summary unavailable without log export")
    return {"source": "hostinger", "window": {"start": date, "end": date, "days": 1},
            "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "metrics": metrics, "findings": [], "errors": errors}


def run(date, reports=REPORTS, token=None, username=None, opener=urlopen):
    doc = check(date, token if token is not None else os.environ.get("HOSTINGER_API_TOKEN", ""),
                username if username is not None else os.environ.get("HOSTINGER_USERNAME", ""), opener)
    out = pathlib.Path(reports) / "data" / date / "hostinger.metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    return doc


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    result = run(day)
    print(json.dumps({"metrics": result["metrics"], "errors": result["errors"]}, indent=2))
