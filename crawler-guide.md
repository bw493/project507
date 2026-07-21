# crawl_directory.py

A small, polite web crawler that collects **company names** and **public website
URLs** from a paginated directory listing and appends them to a CSV. It walks the
listing one page at a time, following the "next page" link until the listing ends.

The crawler deliberately collects names and website URLs only. It does not gather
email addresses or any other contact information.

## Requirements

- Python 3.10 or newer
- Dependencies:

  ```
  pip install requests beautifulsoup4
  ```

## Usage

```
python crawl_directory.py --url "<listing-page-url>" [options]
```

Always start with `--dry-run`. It performs the full crawl and prints every
company it would add, without writing anything to disk, so you can confirm the
selectors and the page-to-page advance before committing to a real run. Remove
`--dry-run` to write the rows.

### Arguments

| Argument | Required | Default | Description |
| --- | --- | --- | --- |
| `--url` | yes | — | The first page of the directory listing. |
| `--card-selector` | no | `.company-card` | CSS selector for each company entry on the page. |
| `--name-selector` | no | `h3` | CSS selector for the company name, relative to a card. |
| `--link-selector` | no | `a[href^='http']` | CSS selector for the website link, relative to a card. |
| `--next-selector` | no | `a[rel='next']` | CSS selector for the "next page" link. The script follows this element's `href`. |
| `--max-pages` | no | `25` | Safety cap on how many pages to follow. |
| `--category` | no | *(empty)* | Value written to the Category column. |
| `--tier` | no | `C` | Value written to the Tier column (`A`, `B`, or `C`). |
| `--dry-run` | no | off | Print what would be added without writing the CSV. |

### Example

```
python crawl_directory.py \
  --url "https://example.com/start-up-map" \
  --card-selector "div.collection-item-7" \
  --name-selector "h4.heading-44" \
  --link-selector "a.submit-button.map" \
  --next-selector "a.w-pagination-next" \
  --category "Neurotech" \
  --tier B \
  --dry-run
```

## How it works

1. **robots.txt is checked first, and per page.** The crawler reads the host's
   `robots.txt` once (cached), then evaluates `can_fetch` for each page URL it
   visits. If a page is disallowed for the crawler's user agent, it stops there.
2. **Each page is fetched with a fixed delay.** Every request is spaced by a
   built-in delay and sends an identifying User-Agent string.
3. **Cards are parsed.** For each element matched by `--card-selector`, the name
   is read from `--name-selector` and the website from `--link-selector`. Website
   links are normalised to a clean root domain, and links back into the directory
   itself or to common social platforms are discarded.
4. **The next page is followed.** The `href` of the `--next-selector` element is
   resolved to an absolute URL and fetched. A page already visited is never
   fetched again, which prevents loops when a final page's "next" control points
   back to itself.
5. **Results are de-duplicated and written.** Companies are de-duplicated across
   the whole crawl, and again against any rows already present in the output CSV,
   so re-running is safe and will not create duplicates.

## Pagination and its limits

The crawler paginates by **following a link** — it reads the `href` of the
`--next-selector` element. This works whenever the next page is a real link (an
`<a>` with an `href`, or `?page=2`-style navigation), which covers most
server-rendered directories.

It does **not** work when:

- "Next" is a `<button>` that only runs JavaScript and carries no `href`, or
- the listing itself is rendered client-side after page load.

Symptoms of these cases are `--card-selector` matching nothing on page one, or
`--next-selector` matching nothing even though a Next control is visible in the
browser. When that happens, the two alternatives are to locate the underlying
data request (often JSON, sometimes with an explicit page/offset/cursor
parameter) via the browser's DevTools Network tab, or to render the page with a
headless browser such as Playwright, which can click a JavaScript "Next" button.

## Before you run it

Read the target site's Terms of Use and confirm that automated collection is
permitted. The crawler is deliberately conservative — public names and URLs only,
robots.txt-respecting, and rate-limited — but honouring the site's stated terms
is your responsibility.
