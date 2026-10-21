# Dry-run fixtures

`Client(dry_run=True)` (`tools/factory/http.py`) answers each provider call with
`<provider>/<call>.json` from this directory, so a `--dry-run` costs nothing and reads no key.
Each file holds at most 10 result items and no secret. SearchAPI files never hold
`search_metadata`, because it echoes the request URL with the key in it. An object with a
top-level `"_status": <int>` is answered with that status and the rest of the object as the body
(`rdap/available.json` is a 404).

Recapture with real calls (this costs real money; keys are read through `factory.secrets`):

    uv run python scripts/capture-fixtures.py [--only searchapi|seranking]

The `arcticshift`, `algolia`, `firecrawl` and `rdap` files were captured from the answers of the
tools' own selftests (`uv run factory <tool> --selftest`), then trimmed: only the fields the tools
read, every Reddit and HN username replaced by `user1`, `user2`... (in `_tags` too), and texts cut
at 400 characters. Every item ID was then replaced by a synthetic one that resolves to nothing
(Reddit `post_01`, `cmt_01`, `t3_thread_01`; HN from `900000001`, beyond any HN item), in the
links inside the texts too, so no anonymised author can be found by looking an ID up.

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
- `arcticshift/posts_search.json`: captured 2026-10-21 from `reddit_mentions --selftest` — query `GET /api/posts/search?query=ad account&subreddit=FacebookAds&after=2026-09-21&limit=10&sort=desc&fields=…` (the 10 newest posts; asked with v1's `fields` list, so without the `permalink` whole items now carry: a dry run rebuilds each item's path; IDs synthetic, `post_01`…`post_10`, and an image link made `https://i.imgur.com/example`)
- `arcticshift/comments_search.json`: captured 2026-10-21 after that selftest — query `GET /api/comments/search?body=ad account&subreddit=FacebookAds&after=2026-10-14&limit=10&sort=desc&fields=…` (the 10 newest comments, without `permalink` likewise; IDs synthetic, `cmt_01`…`cmt_10`, threads `t3_post_05` for the post of `posts_search.json` they answer, `t3_thread_01`… for the others)
- `algolia/search_by_date.json`: captured 2026-10-21 from `hn_mentions --selftest` — query `GET /api/v1/search_by_date?query=ad account&tags=story&numericFilters=created_at_i>1761004800,created_at_i<1792627200&hitsPerPage=10&typoTolerance=false` (10 of 73 stories, without `_highlightResult` and URLs; `objectID`, `story_id` and `story_<id>` tags synthetic from `900000001`, and a link to another item `900000011`; a dry run answers the comments search with it too)
- `firecrawl/scrape.json`: captured 2026-10-21 from `pricing_scan --selftest` — query `POST /v1/scrape` with `{"url": "https://example.com", "formats": ["markdown"], "onlyMainContent": true}` (metadata kept: title, language, URLs, status, content type)
- `rdap/taken.json`: captured 2026-10-21 from `domain_check --selftest` — query `GET https://rdap.org/domain/example.com`, answered 200 by Verisign (notices, links and DNSSEC data dropped); a dry run answers every .com with it
- `rdap/available.json`: hand-written 2026-10-21, `{"_status": 404}`: the registry's 404 for a domain nobody holds, served with an empty body; a dry run answers every domain but a .com with it

The hand-authored files use the documented field names and nesting, and their
`search_parameters` carry the queries `scripts/capture-fixtures.py` makes. Every advertiser,
page, ID and domain in them is invented, and the domains use the reserved `.example` TLD. The Meta
docs example has no `search_parameters`, so that file echoes the request parameters the way the
other engines do.
