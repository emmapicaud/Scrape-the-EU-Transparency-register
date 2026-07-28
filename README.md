# EU Transparency Register Scraper — "Deforestation" Search

This repository contains a Python script that scrapes the [EU Transparency Register](https://transparency-register.europa.eu/) to collect all organisations and entries matching the search term **"deforestation"**, and exports the results to a CSV file for further analysis.

## Overview

The EU Transparency Register lists organisations (companies, NGOs, consultancies, think tanks, etc.) that engage in lobbying or advocacy activities with EU institutions. This script automates the process of querying the register's public search interface, paginating through all result pages, and extracting structured data for each entry.

## What the code does

1. **Query setup**
   The script targets the register's search endpoint (`https://ec.europa.eu/transparencyregister/public/search`) with the query parameters:
   - `lang`: language of the interface (`en`)
   - `queryText`: the search term (`deforestation`)
   - `page`: the page number, used for pagination

   A custom `User-Agent` and `Referer` header are sent with each request to mimic a browser and avoid being blocked by the server.

2. **HTML parsing**
   Each response page is parsed with **BeautifulSoup**. Search results are rendered as `<article class="ecl-content-item">` elements, one per organisation. For each article, the script extracts:
   - **Name** of the organisation (`h1 .ecl-link__label`)
   - **Detail page URL** (`h1 a.ecl-link`, converted to an absolute URL)
   - All key/value pairs found in the description list (`dl`) of the entry, such as:
     - Registration (REG) Number
     - Status
     - Category
     - Location
     - Latest update date

   These fields are collected dynamically (via `dt`/`dd` pairs), so the script adapts automatically if the register adds or removes fields, rather than relying on a fixed schema.

3. **Pagination loop**
   The script iterates over result pages incrementally (`page = 1, 2, 3, ...`), sending a fresh request for each page and stopping automatically once a page returns no `article` elements (i.e., the end of the result set has been reached). This avoids relying on a hardcoded page count and adapts to however many results the query returns.

4. **Data assembly and export**
   All extracted entries are appended to a list of dictionaries, which is then converted into a **pandas DataFrame**. The final dataset is exported to a CSV file (`EU_transparency_scraping.csv`) for reuse outside the script.

5. **Deduplication check**
   As a data-quality check, the script computes the number of unique values in the `REG Number` column (`df["REG Number"].nunique()`) to verify how many distinct organisations were actually captured, since the same organisation could in principle appear more than once across paginated results.

## Requirements

```
requests
beautifulsoup4
pandas
```

Install with:
```bash
pip install requests beautifulsoup4 pandas
```

## Usage

Run the script directly:
```bash
python scrape_transparency_register.py
```

The script will:
1. Print the HTTP status code and a preview of the page structure for the first request.
2. Loop through all available result pages for the query "deforestation".
3. Print progress (`Page X: N résultats`) as it goes.
4. Save the collected data to `EU_transparency_scraping.csv`.
5. Print the total number of entries collected and the number of unique organisations (by REG Number).

## Output

The resulting CSV contains one row per organisation entry, with columns typically including:

| Column | Description |
|---|---|
| `name` | Organisation name |
| `detail_url` | Link to the organisation's detail page on the register |
| `REG Number` | Unique EU Transparency Register identifier |
| `Status` | Registration status |
| `Category` | Type of organisation (e.g., company, NGO, think tank) |
| `Location` | Registered location |
| `Latest update` | Date of the last update to the entry |

*(Exact column names depend on the fields present on the register's site at the time of scraping.)*

### Sample output

Below is an illustrative example of what a few rows of `EU_transparency_scraping.csv` look like (values are fictional, for illustration only):

| name | detail_url | REG Number | Status | Category | Location | Latest update |
|---|---|---|---|---|---|---|
| Example Forest Watch NGO | `https://ec.europa.eu/transparencyregister/public/.../123456789012-34` | 123456789012-34 | Registered | Non-governmental organisations, platforms and networks and similar | Brussels, Belgium | 12/03/2026 |
| Example Timber Trade Association | `https://ec.europa.eu/transparencyregister/public/.../567890123456-78` | 567890123456-78 | Registered | Trade and business associations | Paris, France | 28/01/2026 |
| Example Sustainability Consultancy | `https://ec.europa.eu/transparencyregister/public/.../901234567890-12` | 901234567890-12 | Registered | Professional consultancies | Berlin, Germany | 05/02/2026 |

Each row corresponds to one organisation entry returned by the search, with one column per field displayed on its registry

## Limitations & possible improvements

- The script currently targets a single search term (`"deforestation"`); it could be generalized to accept the query as a parameter or loop over multiple search terms.
- No retry/error-handling logic is implemented for failed requests (e.g., timeouts, rate limiting) — adding retries with backoff would make the scraper more robust for large-scale or repeated runs.
- No delay is added between requests; adding a short pause between page requests would be more respectful of the server and reduce the risk of being throttled or blocked.
- The script does not currently visit each organisation's detail page (`detail_url`) to extract additional information (e.g., financial data, meetings with EU officials) — this could be a natural next step.

## Disclaimer

This script queries a publicly accessible EU institutional website. Users should review the [EU Transparency Register's terms of use](https://transparency-register.europa.eu/) and applicable robots.txt / terms of service before running large-scale scrapes, and should scrape responsibly (reasonable request rate, respecting any usage restrictions).

## License
The code is under MIT License