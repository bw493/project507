#!/usr/bin/env python3
"""
crawl_directory.py — Project 507 target-list builder.

Collects company NAMES and WEBSITE URLs from a public startup directory listing
page and appends them to outreach_tracker.csv as Not Sent rows. Follows the
listing's "next page" link automatically, one page at a time, until no further
page is found (or --max-pages is reached).

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
        --next-selector "a[rel='next']" \
        --max-pages 25 \
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

# robots.txt is identical for every page on a host, so read it once per host
# and reuse the parser. can_fetch() is still evaluated per-URL, because
# different paths within a host may carry different rules.
_ROBOTS_CACHE: dict[str, RobotFileParser | None] = {}


def robots_allows(url: str, user_agent: str = USER_AGENT) -> bool:
    """Return True only if robots.txt explicitly permits fetching `url`."""
    parts = urlparse(url)
    host_key = f"{parts.scheme}://{parts.netloc}"

    if host_key not in _ROBOTS_CACHE:
        robots_url = f"{host_key}/robots.txt"
        parser = RobotFileParser()
        try:
            parser.set_url(robots_url)
            parser.read()
        except Exception as exc:  # no robots.txt reachable
            print(f"  ! could not read {robots_url} ({exc}); refusing to proceed.")
            _ROBOTS_CACHE[host_key] = None
        else:
            _ROBOTS_CACHE[host_key] = parser

    parser = _ROBOTS_CACHE[host_key]
    if parser is None:
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


def find_next_url(html: str, base_url: str, next_sel: str,
                  visited: set[str]) -> str:
    """Locate the "next page" link and return its absolute URL.

    Returns "" when no usable next link is found. This resolves the href of an
    <a> element; it CANNOT trigger a JavaScript-only button that carries no
    href (see NOTE at the bottom of this file). Any candidate that points at an
    already-visited page is rejected, which also guards against a "next" link
    on the final page that points back to itself.
    """
    soup = BeautifulSoup(html, "html.parser")
    link = soup.select_one(next_sel)
    if not link or not link.get("href"):
        return ""

    next_url = urljoin(base_url, link["href"])
    parts = urlparse(next_url)
    if parts.scheme not in ("http", "https"):
        return ""
    if next_url.split("#")[0] in visited:
        return ""
    return next_url


def crawl(start_url: str, card_sel: str, name_sel: str, link_sel: str,
          next_sel: str, max_pages: int) -> list[dict]:
    """Walk the listing page by page, following the "next" link each time.

    Returns the de-duplicated list of companies gathered across every page. A
    company seen on more than one page (common when listings overlap at page
    boundaries) is kept only once.
    """
    collected: list[dict] = []
    seen_companies: set[str] = set()
    visited: set[str] = set()
    url = start_url
    page = 0

    while url and page < max_pages:
        canonical = url.split("#")[0]
        if canonical in visited:
            print("  ! next link revisits an earlier page; stopping to avoid a loop.")
            break
        visited.add(canonical)
        page += 1

        # robots.txt can differ by path, so re-check every page (cached per host).
        if not robots_allows(url):
            print(f"  robots.txt disallows page {page} ({url}). Stopping here.")
            print("  Build any remaining pages of the list by hand instead.")
            break

        print(f"Fetching page {page}: {url}")
        try:
            html = fetch(url)
        except requests.RequestException as exc:
            print(f"  request failed: {exc}")
            break

        rows = parse_listing(html, url, card_sel, name_sel, link_sel)
        new_on_page = 0
        for row in rows:
            key = row["Company"].strip().lower()
            if key and key not in seen_companies:
                seen_companies.add(key)
                collected.append(row)
                new_on_page += 1
        print(f"  parsed {len(rows)} companies on this page "
              f"({new_on_page} new, {len(collected)} total so far).")

        url = find_next_url(html, url, next_sel, visited)

    if url and page >= max_pages:
        print(f"  reached --max-pages limit ({max_pages}); stopping early. "
              f"Raise --max-pages if more pages remain.")
    elif not url:
        print("  no further 'next' link found; reached the end of the listing.")

    return collected


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
    ap.add_argument("--url", required=True, help="Directory listing page (first page)")
    ap.add_argument("--card-selector", default=".company-card",
                    help="CSS selector for each company card")
    ap.add_argument("--name-selector", default="h3",
                    help="CSS selector for the name, relative to the card")
    ap.add_argument("--link-selector", default="a[href^='http']",
                    help="CSS selector for the website link, relative to the card")
    ap.add_argument("--next-selector", default="a[rel='next']",
                    help="CSS selector for the 'next page' link. The script "
                         "follows this element's href; it cannot click a "
                         "JavaScript-only button (see NOTE at end of file).")
    ap.add_argument("--max-pages", type=int, default=25,
                    help="Safety cap on how many pages to follow (default: 25)")
    ap.add_argument("--category", default="", help="Value for the Category column")
    ap.add_argument("--tier", default="C", choices=["A", "B", "C"])
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would be added without writing the CSV")
    args = ap.parse_args()

    rows = crawl(args.url, args.card_selector, args.name_selector,
                 args.link_selector, args.next_selector, args.max_pages)
    print(f"\nCollected {len(rows)} unique companies across all pages.")

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
# NOTE — pagination, "clicking", and client-side rendering
#
# This script paginates by FOLLOWING a link: it reads the href of the element
# matched by --next-selector and fetches that URL. With `requests` there is no
# browser and therefore nothing to "click". This works whenever the next page
# is a real link (an <a> with an href, or ?page=2 style navigation), which
# covers most server-rendered directories.
#
# It does NOT work when "Next" is a <button> that only runs JavaScript and
# carries no href, or when the whole listing is rendered client-side. Symptoms:
# --card-selector matches nothing on page 1, or --next-selector matches nothing
# even though a Next control is visibly present in the browser. In that case:
#
#   1. Find the underlying data request. Open the page in Chrome, DevTools ->
#      Network -> XHR/Fetch, and reload. The listing (and its pagination) often
#      arrives as JSON, sometimes with an explicit page/offset/cursor parameter.
#      Requesting that endpoint directly is far more reliable, and far lighter
#      on their server, than rendering the page.
#
#   2. Render the page with Playwright (`pip install playwright && playwright
#      install chromium`). Playwright CAN click a JavaScript "Next" button:
#      load the page, click the control, wait for the new cards, call
#      page.content(), and feed each page's HTML into parse_listing() in a loop.
#
# Before either: read the site's Terms of Use. If automated collection is
# prohibited, 40-50 companies is roughly two hours of manual work, and it
# produces better personalization hooks than any parser will.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main())