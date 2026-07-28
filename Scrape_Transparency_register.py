"""
EU Transparency Register Scraper — "deforestation" search
------------------------------------------------------------

This script queries the public search interface of the EU Transparency
Register, collects all entries matching a given search term, and exports
the results to a CSV file.

See README.md for a full description of the methodology.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

SEARCH_URL = "https://ec.europa.eu/transparencyregister/public/search"
QUERY_TEXT = "deforestation"
LANG = "en"
OUTPUT_CSV = "EU_transparency_scraping.csv"
MAX_PAGES = 500  # safety limit; the loop stops earlier once a page is empty

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://transparency-register.europa.eu/"
}


def parse_page(html: str) -> list[dict]:
    """Extract all organisation entries from a single search result page."""
    soup = BeautifulSoup(html, "html.parser")
    entries = []

    for article in soup.select("article.ecl-content-item"):
        entry = {}

        # Organisation name and link to its detail page
        name_tag = article.select_one("h1 .ecl-link__label")
        link_tag = article.select_one("h1 a.ecl-link")

        entry["name"] = name_tag.get_text(strip=True) if name_tag else None
        entry["detail_url"] = (
            "https://ec.europa.eu/transparencyregister/public/" + link_tag["href"]
            if link_tag and link_tag.has_attr("href")
            else None
        )

        # All other fields (REG Number, Status, Category, Location, etc.)
        # are extracted generically from the dt/dd pairs, so the script
        # adapts automatically if the register adds or removes fields.
        for dl in article.select(".ecl-content-block__description dl"):
            dt = dl.select_one(".ecl-description-list__term")
            dd = dl.select_one(".ecl-description-list__definition span")
            if dt and dd:
                entry[dt.get_text(strip=True)] = dd.get_text(strip=True)

        entries.append(entry)

    return entries


def scrape_all_pages() -> pd.DataFrame:
    """Loop over result pages until an empty page is reached."""
    results = []

    for page in range(1, MAX_PAGES):
        params = {
            "lang": LANG,
            "queryText": QUERY_TEXT,
            "page": page
        }

        response = requests.get(SEARCH_URL, params=params, headers=HEADERS)
        page_entries = parse_page(response.text)

        print(f"Page {page}: {len(page_entries)} result(s)")

        if not page_entries:
            break

        results.extend(page_entries)

    return pd.DataFrame(results)


def main():
    df = scrape_all_pages()

    print("Total entries collected:", len(df))
    if "REG Number" in df.columns:
        print("Unique organisations (by REG Number):", df["REG Number"].nunique())

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved results to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()