#!/usr/bin/env python3
"""
Cheap, dependency-free health/SEO monitor for mosaichostels.com.

Exists to gate the expensive Claude-based auto-fix step: this script runs
first and exits non-zero only when it finds something real, so the fix
step doesn't burn API calls on a schedule regardless of whether anything's
actually wrong.

Checks performed (each one maps to a real bug found during the July 2026
SEO audit/fix pass on this site):
  1. HTTP status - every core page and blog post returns 200
  2. Local-vs-live diff - catches silent deploy failures (the homepage
     was once silently overwritten with a blog post's content this way)
  3. JSON-LD validity - every <script type="application/ld+json"> block
     parses as valid JSON on the live page
  4. Nav/footer presence - catches the "dead <div id=containers>" bug
     that left the homepage, /privacy, and all blog posts without a
     rendered navbar/footer
  5. Title uniqueness - catches the "duplicate shell content" bug where
     every blog post served the same generic post.html template
  6. Sitemap XML validity + reachability

No third-party dependencies - stdlib only, so it runs in any CI runner
with no pip/npm install step.
"""

import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SITE = "https://www.mosaichostels.com"
REPO_ROOT = Path(__file__).resolve().parent.parent

CORE_PAGES = [
    ("index.html", "/"),
    ("about.html", "/about"),
    ("contact.html", "/contact"),
    ("gallery.html", "/gallery"),
    ("book-now.html", "/book-now"),
    ("privacy.html", "/privacy"),
]


def find_blog_posts():
    """(local_path, url_path) for every blog/<slug>/index.html in the repo."""
    posts = []
    blog_dir = REPO_ROOT / "blog"
    for entry in sorted(blog_dir.iterdir()):
        if entry.is_dir() and (entry / "index.html").exists():
            posts.append((f"blog/{entry.name}/index.html", f"/blog/{entry.name}/"))
    return posts


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "mosaic-site-monitor/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def check_status_and_diff(local_rel_path, url_path, issues):
    url = SITE + url_path
    local_file = REPO_ROOT / local_rel_path
    if not local_file.exists():
        issues.append(f"LOCAL MISSING: {local_rel_path} does not exist in repo")
        return None

    try:
        status, live_html = fetch(url)
    except urllib.error.HTTPError as e:
        issues.append(f"HTTP {e.code}: {url}")
        return None
    except Exception as e:
        issues.append(f"FETCH FAILED: {url} ({e})")
        return None

    if status != 200:
        issues.append(f"HTTP {status} (expected 200): {url}")
        return None

    local_html = local_file.read_text(encoding="utf-8")
    if local_html.strip() != live_html.strip():
        issues.append(
            f"LIVE/LOCAL MISMATCH: {url} does not match {local_rel_path} "
            f"(deploy may have silently failed for this file)"
        )

    return live_html


def check_jsonld(url, html, issues):
    blocks = re.findall(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S
    )
    for block in blocks:
        try:
            json.loads(block)
        except json.JSONDecodeError as e:
            issues.append(f"INVALID JSON-LD on {url}: {e}")


def check_nav_footer(url, html, issues):
    if 'id="mainNav"' not in html:
        issues.append(f"MISSING NAVBAR: {url} has no rendered <nav id=\"mainNav\">")
    if "footer-tagline" not in html:
        issues.append(f"MISSING FOOTER: {url} has no rendered footer content")


def check_sitemap(issues):
    url = f"{SITE}/sitemap.xml"
    try:
        status, xml_text = fetch(url)
    except Exception as e:
        issues.append(f"SITEMAP UNREACHABLE: {e}")
        return
    if status != 200:
        issues.append(f"SITEMAP HTTP {status}")
        return
    try:
        ET.fromstring(xml_text)
    except ET.ParseError as e:
        issues.append(f"SITEMAP INVALID XML: {e}")


def check_title_uniqueness(titles_by_url, issues):
    seen = {}
    for url, title in titles_by_url.items():
        if title in seen:
            issues.append(
                f"DUPLICATE TITLE: '{title}' appears on both {seen[title]} and {url} "
                f"(possible template-shell regression)"
            )
        else:
            seen[title] = url


def main():
    issues = []
    titles_by_url = {}

    pages = CORE_PAGES + find_blog_posts()

    for local_rel_path, url_path in pages:
        url = SITE + url_path
        html = check_status_and_diff(local_rel_path, url_path, issues)
        if html is None:
            continue
        check_jsonld(url, html, issues)
        check_nav_footer(url, html, issues)
        m = re.search(r"<title>([^<]*)</title>", html)
        if m:
            titles_by_url[url] = m.group(1).strip()
        else:
            issues.append(f"MISSING TITLE TAG: {url}")

    check_title_uniqueness(titles_by_url, issues)
    check_sitemap(issues)

    if issues:
        print(f"::warning::Site monitor found {len(issues)} issue(s)")
        for issue in issues:
            print(f"- {issue}")
        report_path = REPO_ROOT / "monitor-report.txt"
        report_path.write_text("\n".join(issues), encoding="utf-8")
        print(f"\nReport written to {report_path}")
        sys.exit(1)
    else:
        print(f"OK - checked {len(pages)} pages, sitemap, JSON-LD, nav/footer, titles. No issues found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
