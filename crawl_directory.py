#!/usr/bin/env python3
"""
crawl_directory.py — Project 507 target-list builder.

Collects company NAMES and WEBSITE URLs from a public startup directory listing
page and appends them to outreach_tracker.csv as Not Sent rows.

Scope, deliberately:
  - Company names and public website URLs only.
  - No email addresses. Contact discovery stays manual (see README of the plan).
  - Honours robots.txt, identifies itself, and rate-limits every request.

Usage:
    python crawl_directory.py --url "https://example.com/start-up-map" --dry-run
    python crawl_directory.py --url "https://example.com/start-up-map" \
        --card-selector ".company-card" \
        --name-selector "h3" \
        --link-selector "a[href^='http']" \
        --category "BCI" --tier B

Dependencies:
    pip install requests beautifulsoup4
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

TRACKER = Path("outreach_tracker.csv")
USER_AGENT = (
    "CruX-UCLA-Project507-Research/1.0 "
    "(student organisation outreach research; contact: brian@example.com)"
)
DELAY_SECONDS = 2.0  # be a good citizen; do not lower this

COLUMNS = [
    "Company", "Website", "Category", "Tier", "Contact Name", "Role", "Email",
    "Personalization Hook", "Date Sent", "Bump 1 Date", "Bump 2 Date",
    "Status", "Notes", "Handoff Owner",
]


def robots_allows(url: str, user_agent: str = USER_AGENT) -> bool:
    """Return True only if robots.txt explicitly permits fetching `url`."""
    parts = urlparse(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    parser = RobotFileParser()
    try:
        parser.set_url(robots_url)
        parser.read()
    except Exception as exc:  # no robots.txt reachable
        print(f"  ! could not read {robots_url} ({exc}); refusing to proceed.")
        return False
    return parser.can_fetch(user_agent, url)


def fetch(url: str) -> str:
    time.sleep(DELAY_SECONDS)
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    response.raise_for_status()
    return response.text


def normalise_website(href: str, base_url: str) -> str:
    """Reduce a link to a clean root domain, dropping tracking parameters."""
    absolute = urljoin(base_url, href)
    parts = urlparse(absolute)
    if parts.scheme not in ("http", "https"):
        return ""
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return f"https://{host}"


def is_external(website: str, base_url: str) -> bool:
    """Filter out links back into the directory itself and social platforms."""
    host = urlparse(website).netloc
    directory_host = urlparse(base_url).netloc.replace("www.", "")
    noise = (
        "linkedin.com", "twitter.com", "x.com", "facebook.com",
        "instagram.com", "youtube.com", "crunchbase.com", directory_host,
    )
    return bool(host) and not any(host.endswith(n) for n in noise)


def parse_listing(html: str, base_url: str, card_sel: str,
                  name_sel: str, link_sel: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select(card_sel)
    if not cards:
        print(f"  ! no elements matched --card-selector '{card_sel}'.")
        print("    The page is likely rendered client-side; see NOTE at the "
              "bottom of this file.")
        return []

    found = []
    for card in cards:
        name_el = card.select_one(name_sel)
        link_el = card.select_one(link_sel)
        if not name_el:
            continue
        name = re.sub(r"\s+", " ", name_el.get_text(strip=True))
        website = ""
        if link_el and link_el.get("href"):
            candidate = normalise_website(link_el["href"], base_url)
            if is_external(candidate, base_url):
                website = candidate
        if name:
            found.append({"Company": name, "Website": website})
    return found


def load_existing() -> set[str]:
    if not TRACKER.exists():
        return set()
    with TRACKER.open(newline="", encoding="utf-8") as f:
        return {row["Company"].strip().lower() for row in csv.DictReader(f)}


def append_rows(rows: list[dict], category: str, tier: str, source: str) -> int:
    existing = load_existing()
    new_file = not TRACKER.exists()

    written = 0
    with TRACKER.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if new_file:
            writer.writeheader()
        for row in rows:
            if row["Company"].strip().lower() in existing:
                continue
            existing.add(row["Company"].strip().lower())
            writer.writerow({
                **{c: "" for c in COLUMNS},
                "Company": row["Company"],
                "Website": row["Website"],
                "Category": category,
                "Tier": tier,
                "Status": "Not Sent",
                "Notes": f"Auto-collected from {source}",
                "Handoff Owner": "Brian Wu",
            })
            written += 1
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", required=True, help="Directory listing page")
    ap.add_argument("--card-selector", default=".company-card",
                    help="CSS selector for each company card")
    ap.add_argument("--name-selector", default="h3",
                    help="CSS selector for the name, relative to the card")
    ap.add_argument("--link-selector", default="a[href^='http']",
                    help="CSS selector for the website link, relative to the card")
    ap.add_argument("--category", default="", help="Value for the Category column")
    ap.add_argument("--tier", default="C", choices=["A", "B", "C"])
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would be added without writing the CSV")
    args = ap.parse_args()

    print(f"Checking robots.txt for {args.url} ...")
    if not robots_allows(args.url):
        print("  robots.txt disallows this path for our user agent. Stopping.")
        print("  Build this portion of the list by hand instead.")
        return 1
    print("  allowed.")

    print("Fetching ...")
    try:
        html = fetch(args.url)
    except requests.RequestException as exc:
        print(f"  request failed: {exc}")
        return 1

    rows = parse_listing(html, args.url, args.card_selector,
                         args.name_selector, args.link_selector)
    print(f"Parsed {len(rows)} companies.")

    if args.dry_run:
        for row in rows:
            print(f"  {row['Company']:<40} {row['Website']}")
        print("\n(dry run — nothing written)")
        return 0

    written = append_rows(rows, args.category, args.tier,
                          urlparse(args.url).netloc)
    print(f"Appended {written} new rows to {TRACKER} "
          f"({len(rows) - written} already present).")
    print("Review the rows, then: git add outreach_tracker.csv && git commit")
    return 0


# ---------------------------------------------------------------------------
# NOTE — if --card-selector matches nothing
#
# Many modern directory pages (the Neurofounders map among them, most likely)
# render their listings in JavaScript after page load, so the HTML that
# `requests` receives contains no company cards at all. Two options:
#
#   1. Find the underlying data request. Open the page in Chrome, DevTools ->
#      Network -> XHR/Fetch, and reload. The listing usually arrives as a
#      single JSON response. If so, request that URL directly and parse it with
#      `response.json()` — far more reliable, and far lighter on their server,
#      than rendering the page.
#
#   2. Render the page with Playwright (`pip install playwright && playwright
#      install chromium`), then feed `page.content()` into parse_listing().
#
# Before either: read the site's Terms of Use. If automated collection is
# prohibited, 40-50 companies is roughly two hours of manual work, and it
# produces better personalization hooks than any parser will.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main())
