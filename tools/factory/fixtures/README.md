# Dry-run fixtures

`Client(dry_run=True)` (`tools/factory/http.py`) answers each provider call with
`<provider>/<call>.json` from this directory, so a `--dry-run` costs nothing and reads no key.
Each file holds at most 10 result items and no secret. SearchAPI files never hold
`search_metadata`, because it echoes the request URL with the key in it.

Recapture with real calls (this costs real money; keys are read through `factory.secrets`):

    uv run python scripts/capture-fixtures.py [--only searchapi|seranking]

## Provenance

- `seranking/analyze_keywords.json`: captured 2026-10-21 — query `POST /research/us/analyze-keywords/` with `["facebook ad account hacked", "business manager hacked"]` (SE Ranking has data for neither, so both rows are `is_data_found: false`)
- `seranking/domain_keywords.json`: captured 2026-10-21 — query `GET /research/us/keywords/?domain=hootsuite.com&limit=60` (the first 10 of 60 rows)
- `seranking/domain_advertising.json`: captured 2026-10-21 — query `GET /research/us/advertising/?domain=hootsuite.com` (the first 10 of 100 rows)
- `seranking/domain_overview.json`: captured 2026-10-21 — query `GET /research/us/overview/?domain=hootsuite.com`
- `searchapi/google.json`: hand-authored 2026-10-21 from https://www.searchapi.io/docs/google; recapture when a SearchAPI key with quota exists
- `searchapi/meta_ad_library.json`: hand-authored 2026-10-21 from https://www.searchapi.io/docs/meta-ad-library-api; recapture when a SearchAPI key with quota exists
- `searchapi/tiktok_ads_library.json`: hand-authored 2026-10-21 from https://www.searchapi.io/docs/tiktok-ads-library-api; recapture when a SearchAPI key with quota exists
- `searchapi/google_ads_transparency_center.json`: hand-authored 2026-10-21 from https://www.searchapi.io/docs/google-ads-transparency-center-api; recapture when a SearchAPI key with quota exists
- `searchapi/linkedin_ad_library.json`: hand-authored 2026-10-21 from https://www.searchapi.io/docs/linkedin-ad-library-api; recapture when a SearchAPI key with quota exists

The hand-authored files use the documented field names and nesting, and their
`search_parameters` carry the queries `scripts/capture-fixtures.py` makes. Every advertiser,
page, ID and domain in them is invented, and the domains use the reserved `.example` TLD. The Meta
docs example has no `search_parameters`, so that file echoes the request parameters the way the
other engines do.
