# Detecting top and newly rising advertisers on the major ad platforms (Meta, Google, TikTok, LinkedIn, Microsoft, Snapchat, Pinterest, Reddit): a feasibility map, October 2026

Checked on 2026-10-22. Tags used below: **[doc]** = the platform's own documentation, read today; **[live check]** = I (or a helper agent, when marked) downloaded or called the public endpoint myself today, with no key and no cost; **[vendor]** = the source sells a competing tool; **[snippet]** = seen only in search-result text, page not opened; **[local note]** = the founder's own v1 ad-intel notes (`~/wrk/pers/personal_skills_and_tools/skills/generic/ad-intel/SKILL.md`), whose endpoints that tooling verified on 2026-09-27, not re-verified today unless marked. Third-party tool prices come from the sibling file `ad_intel_tools_pricing.md` (helper, read 2026-10-22) and are only summarised in section 5. Money is in the source's currency.

## 1. Meta Ad Library API (`ads_archive`): access, fields, search, limits, enumeration, and estimating spend from reach

### Takeaway
Meta's official API is free and returns every commercial ad that reached an EU (or UK) location, with an estimated reach per ad (`eu_total_reach`), reach by age × gender × country, targeting, payer and beneficiary, and delivery dates. It returns **no spend and no impressions for commercial ads**; those fields exist only for political and issue ads, which Meta stopped selling in the EU in October 2025. For countries with no EU delivery, including the US, the API returns political ads only. US commercial ads can therefore be read only from the web library, through scrapers such as SearchAPI. The web library gives start dates, active status, variant counts and an order sorted by impressions, but no numbers. A spend figure for France has to be modelled as reach × assumed frequency × CPM. Vendor benchmarks for 2026 put the Meta CPM at about $7–9 in France and $16–23 in the US.

### Cited Findings

#### Endpoint, search parameters, pagination [doc]
- Read-only endpoint `GET https://graph.facebook.com/<VERSION>/ads_archive`; the reference page covers v26.0 — [Meta ads_archive reference](https://developers.facebook.com/docs/graph-api/reference/ads_archive/)
- Only `ad_reached_countries` is required (`ALL` or ISO codes). Paraphrase of the doc note: an ad that reached no EU location is returned only if it is a political, electoral or social-issue ad — [same](https://developers.facebook.com/docs/graph-api/reference/ads_archive/)
- Search parameters:
  - `search_terms`: default empty string, max 100 characters, a space means AND. `search_type`: `KEYWORD_UNORDERED` (default) or `KEYWORD_EXACT_PHRASE`.
  - `search_page_ids`: up to 10 page IDs.
  - `ad_active_status`: `ACTIVE` by default, or `INACTIVE` or `ALL`.
  - `ad_delivery_date_min` and `ad_delivery_date_max`: `YYYY-mm-dd`, inclusive.
  - `ad_type`: `ALL` by default, or `EMPLOYMENT_ADS`, `FINANCIAL_PRODUCTS_AND_SERVICES_ADS`, `HOUSING_ADS`, `POLITICAL_AND_ISSUE_ADS`.
  - Also `languages`, `media_type`, `publisher_platforms` (FACEBOOK, INSTAGRAM, AUDIENCE_NETWORK, MESSENGER, WHATSAPP, OCULUS, THREADS, STREAMING_SERVICES) and `unmask_removed_content`.
  - `bylines`, `delivery_by_region` and `estimated_audience_size_min/max` work for political ads only.
  - Source: [same](https://developers.facebook.com/docs/graph-api/reference/ads_archive/)
- Errors and paging:
  - Error 613 means the rate limit was exceeded; the reference publishes no numeric limit.
  - Error 190 is an invalid token, 100 an invalid parameter, 2500 a query that failed to parse.
  - Paging uses the Graph API `paging` cursors, and an empty `data` marks the end.
  - Source: [same](https://developers.facebook.com/docs/graph-api/reference/ads_archive/)

#### Returned fields (ArchivedAd) and the absence of a spend field for commercial ads [doc]
- **Political and issue ads only:** `spend` and `impressions` (InsightsRangeValue ranges: spend from under 100 to over 1M in `currency`, impressions from under 1,000 to over 1M), `currency`, `bylines`, `demographic_distribution`, `delivery_by_region`, `estimated_audience_size` — [ArchivedAd reference](https://developers.facebook.com/docs/marketing-api/reference/archived-ad/)
- **"Available only for ads delivered to the EU":** `eu_total_reach` (int32, estimated total reach across the EU) and `beneficiary_payers` — [same](https://developers.facebook.com/docs/marketing-api/reference/archived-ad/)
- **UK and EU ads (and political ads delivered in Brazil):** `age_country_gender_reach_breakdown`, `target_ages`, `target_gender`, `target_locations` (places included or excluded). `br_total_reach` is for Brazil political ads — [same](https://developers.facebook.com/docs/marketing-api/reference/archived-ad/)
- **No availability restriction stated:**
  - `id` and `ad_creation_time` (when the ad was created, not when it ran).
  - `ad_delivery_start_time`, and `ad_delivery_stop_time` (blank means it runs until stopped).
  - `ad_creative_bodies`, `ad_creative_link_captions`, `ad_creative_link_descriptions`, `ad_creative_link_titles`.
  - `ad_snapshot_url`, `languages`, `page_id`, `page_name`, `publisher_platforms`.
  - `total_reach_by_location`, with "Currently supported locations: EU, BR, and UK".
  - Source: [same](https://developers.facebook.com/docs/marketing-api/reference/archived-ad/)
- Commercial ads therefore have no spend field in any country. A vendor confirms that standard commercial ads show no spend, budget or CPM, and that spend ranges exist only for political, electoral and issue ads — [Adnova, updated 2026-10-06](https://adnova.ai/blogs/find-competitors-meta-adspend) [vendor]
- EU ads appear in the archive from 17 Aug 2023: "On the 17.08.2023 all EU ads since that date appeared in the database" — [Lejo1/facebook_ad_library README](https://github.com/Lejo1/facebook_ad_library). DSA Art. 39 retention runs "until one year after the advertisement was presented for the last time" — [Art. 39 text](https://www.eu-digital-services-act.com/Digital_Services_Act_Article_39.html)

#### Access requirements
- Meta's own access page (`facebook.com/ads/library/api`) returned 403 to an automated fetch, so these steps come from vendors [vendor] — [Gethookd guide, 2026-09-09](https://www.gethookd.ai/learn/how-to-use-meta-ad-library-api-access-token-generation-documentation/):
  - confirm identity and country of residence with a government ID at facebook.com/ID (about 1–3 business days);
  - create a Meta developer app of the Business type;
  - generate a user token with `ads_read` in the Graph API Explorer;
  - short-lived tokens last about 1–2 hours, long-lived ones 60 days, and calls are free.
- Another vendor says access depends on accepting Meta's "Authorized Access to Public Information" terms, that the identity check stays with the personal account that created the token, and that building targeting or resale products on the data breaches the terms — [singhamandeep.com](https://singhamandeep.com/?p=1356) [snippet]
- On 16 Oct 2024 Meta asked the maintainer of an open archive of the library to take public dumps down. The data "may only be provided to people who themselves have verified to access the Facebook Ad Library API". The maintainer also reports a "maximum of 15 apps" rule that "drastically reduced the rate limit" — [Lejo1/facebook_ad_library README](https://github.com/Lejo1/facebook_ad_library) (repository last pushed 2026-09-13)

#### Rate limits
- No official number; the reference lists only error 613 — [Meta ads_archive reference](https://developers.facebook.com/docs/graph-api/reference/ads_archive/)
- Vendor and tooling figures:
  - "heavily rate-limited", with a practical page size of "a few hundred" — [Gethookd](https://www.gethookd.ai/learn/how-to-use-meta-ad-library-api-access-token-generation-documentation/) [vendor];
  - `limit` "max 1000" per page — [Adligator, 2026-02-14](https://adligator.com/blog/meta-ad-library-api-competitor-monitoring) [vendor];
  - the academic AdDownloader package uses `limit` 300 and three retries with exponential backoff — [AdDownloader docs](https://addownloader.readthedocs.io/en/latest/adlib_api.html);
  - quotas are kept per access token, and a 429 means waiting about 60 s — [Zernio docs](https://docs.zernio.com/platforms/meta-ads/ad-library) [snippet].

#### Can one enumerate every advertiser active in a country?
- AdDownloader requires either `search_terms` or page IDs, plus country and dates — [AdDownloader docs](https://addownloader.readthedocs.io/en/latest/adlib_api.html)
- An open-source crawler enumerates the whole library with a wildcard:
  - "Since V3 the ads are crawled using an empty query (*) across all countries. This query turned out to be quiet [sic] reliable and returns all ads of all pages."
  - With the reduced rate limit, its V7 notes say "The database is incomplete for sure".
  - Source: [Lejo1/facebook_ad_library README](https://github.com/Lejo1/facebook_ad_library)
- Meta's own research script repository passes `-s '.'` as the search term in its example — [facebookresearch/Ad-Library-API-Script-Repository](https://github.com/facebookresearch/Ad-Library-API-Script-Repository)
- Sciences Po médialab's `DSA-facebook-ads` repository (created 2025-01-24) works from that dump. It keeps French-targeted ads by searching `age_country_gender_reach_breakdown` for `"country": "FR"` — [medialab/DSA-facebook-ads](https://github.com/medialab/DSA-facebook-ads) [live check via the GitHub API]
- The downloadable "Ad Library Report" (spend per advertiser) covers political and issue pages only — [Lejo1 README, V2 notes](https://github.com/Lejo1/facebook_ad_library)

#### The web Ad Library (the only window on US commercial ads)
- Without a login, the web library lists every active ad worldwide. It shows start date, copy, headline, display domain and CTA, and states result counts such as "~63 results". The reach table appears only for EU delivery ("EU ad delivery — Reach", age × gender × country) [local note]
- Since about January 2026 the library offers a sort by total impressions (URL parameter `sort_data[mode]=total_impressions`) beside "Most recent" — [Coinis, 2026-01-31](https://coinis.com/blog/meta-changed-the-ads-library-and-its-a-big-deal) [vendor]. SearchAPI's Meta engine sorts by `impressions_high_to_low` by default — [SearchAPI docs](https://www.searchapi.io/docs/meta-ad-library-api)
- Sources conflict on whether impression bands are now displayed for commercial ads:
  - some 2026 vendor guides describe bands from under 1K to 1M+ for the whole library, with a "low impression count" flag under 100 [snippet];
  - AdWhispr lists commercial impressions as hidden — [AdWhispr, 2026-05-20](https://adwhispr.com/blog/meta-ad-library-guide-2026) [vendor];
  - SearchAPI's scraped `impressions_with_index.impressions_index` is −1 in every documented example — [SearchAPI docs](https://www.searchapi.io/docs/meta-ad-library-api)

#### Estimating spend from reach, and CPM benchmarks for France vs the US
- Practitioner formula: "Estimated Spend = (Reach × Frequency ÷ 1,000) × CPM" — [Adnova, updated 2026-10-06](https://adnova.ai/blogs/find-competitors-meta-adspend) [vendor]
  - Frequency: "Most prospecting ads land between 1.5 and 2.5 over their lifetime… Use 1.8 as a sane default and state it openly" (unsourced).
  - "Plugging a US benchmark into an EU reach figure inflates the estimate badly"; "Do not extrapolate blindly to global spend".
- Other methods, which its authors call rough — [Adligator, 2026-02-15](https://adligator.com/blog/estimate-competitor-facebook-ad-spend) [vendor]:
  - scale EU spend by (total active ads ÷ EU-targeted ads);
  - back-calculate impressions from engagement, assuming a 0.5–1.5% engagement rate (unsourced);
  - map volume and longevity to bands (<$5K, $5K–25K, $25K+/mo), which it concedes "is a heuristic, not a formula".
- Off-the-shelf version: Trendtrack sells "reach and budget (spend) estimates for EU ads, based on Meta's transparency disclosures" from about $34/mo billed yearly; the method is unpublished — [Trendtrack pricing](https://www.trendtrack.io/pricing) (via the helper file)
- Meta CPM benchmarks:

| Source | France | US | Notes |
|---|---|---|---|
| [Lebesgue](https://lebesgue.io/facebook-ads/facebook-cpm-by-country) | $6.95 | $16.08 | Ecommerce benchmark posted 2026-07-27, sample size not stated; also DE $9.05, UK $11.81, ES $6.65, IT $6.06 |
| [Adamigo](https://www.adamigo.ai/blog/meta-ads-cpm-cpc-benchmarks-by-country-2026) [snippet] | $8.05 (typical $6.50–9.50) | $23.00 | Forecast built on late-2025 data |
| [Stackmatix](https://www.stackmatix.com/blog/facebook-ads-cpm-by-country-2026) [snippet] | $6.80–11.20 | $10.50–16.80 | Q1 2026 |
| [Adligator](https://adligator.com/blog/meta-ads-cpm-by-country-benchmarks) [snippet] | $7–10 (Facebook), $9–13 (Instagram) | $16–21 | US above $30 in Black Friday week |
| [La Fabrique du Net](https://www.lafabriquedunet.fr/logiciels/tendances/facebook-linkedin-instagram-twitter-quel-est-le-cout-dune-annonce) [snippet] | €8–18 (Facebook), €10–20 (Instagram) | — | France 2026 |
| [AdSpendSpy](https://www.adspendspy.com/facebook-cpm-by-country) [snippet] | €7.46 (band €6.20–8.30) | ≈ €10.65 | Modelled; the US figure is EU data × 1.5 |

### Inferences
- In France and the EU, the API alone can produce a weekly ranking of who gained the most reach, at no cost. It needs one step: store each ad's cumulative `eu_total_reach` (or its FR share from `age_country_gender_reach_breakdown`) every week and take the differences. The API reports reach over an ad's lifetime, not per week.
- An untested calibration: political and issue ads in the archive carry spend and impression ranges, and EU reach as well. Their impressions ÷ reach gives an empirical frequency for France, and spend ÷ impressions an empirical CPM. Use the 2023–2025 history, since EU political ads stopped in October 2025. Political audiences and CPMs differ from commercial ones, so treat the result as an order of magnitude.
- For the US, Meta offers no commercial exposure numbers. The proxies are:
  - active ads per page;
  - new ads per week, from start dates;
  - variant counts (`collation_count`);
  - rank under the impressions sort.

  All of these come from scraping the web library, through SearchAPI or similar.
- Spend estimates swing by about 1.7× from the frequency assumption (1.5–2.5) and about 1.4× from the choice of CPM source (France $6.95–9.50), so about 2.3× combined. Report them as ranges and rank advertisers on reach deltas rather than on modelled euros.

### Gaps
- I could not read Meta's access page or the Ad Library API terms (403). The identity-confirmation steps and terms come from vendors and one open-source maintainer.
- No official rate-limit number. Whether `search_terms='*'` still enumerates everything rests on one maintainer, not on Meta.
- How fast `eu_total_reach` updates while an ad runs is undocumented.
- Whether the web library now shows impression bands for US commercial ads is unresolved: sources conflict. The way to settle it is to open the library logged out.

## 2. Google Ads Transparency Center: is there an API? The BigQuery public dataset, its schema, coverage, update cadence, cost and an example query

### Takeaway
Google offers **no official REST API, but an official bulk dataset does exist**: the BigQuery public dataset `bigquery-public-data.google_ads_transparency_center`, with tables `creative_stats` and `removed_creative_stats`. The same data downloads as JSON shards from a public Cloud Storage bucket.
- **Coverage:** creatives served in the **EEA and Turkey only**, so not the US.
- **Per country:** first and last shown dates, plus impression ranges (lower and upper bounds), also broken down by surface (Search, YouTube, Shopping, Maps, Play).
- **Per creative:** a vertical `topic` (56 values seen), advertiser identity and verification status, and targeting flags.

I checked that the export was rewritten today (2026-10-22). Dates are fresh, with a one-day lag, but **impression figures lag 90 days**. A weekly France query scans an estimated 30–80 GB, inside BigQuery's free 1 TiB a month.
- **What it can rank:** new entrants and "creative velocity" (new creatives per week) per advertiser and topic in France, on fresh data.
- **What it cannot rank:** impression growth over the last 30 days. The impression series it can build is three months old.

### Cited Findings

#### Official documentation [doc]
- The dataset README describes it:
  - `creative_stats` covers the EEA and Turkey; `removed_creative_stats` covers the EEA only.
  - Downloads "may be split across several JSON files"; the README file itself was updated 2026-03-18.
  - Both are governed by the Google Terms of Service and the "Google Ads Transparency Center Additional Terms" (https://adstransparency.google.com/terms).
  - Source: [README](https://storage.googleapis.com/ads-transparency-center/api-data/README.txt)
- Listing: [Google Cloud Marketplace](https://console.cloud.google.com/marketplace/details/bigquery-public-data/google-ads-transparency-center)
- `creative_stats` fields — [README](https://storage.googleapis.com/ads-transparency-center/api-data/README.txt):
  - Advertiser and creative: `advertiser_id`, `creative_id`, `creative_page_url`, `ad_format_type`, `advertiser_disclosed_name`, `advertiser_legal_name`, `advertiser_location`, `advertiser_verification_status`.
  - `region_stats[]`, one entry per region:
    - `region_code`: a country code, or the `EEA` aggregate.
    - `first_shown`: "Anything before 2023-03-01 is reported as 2023-03-01".
    - `last_shown`.
    - `times_shown_start_date` and `times_shown_end_date`.
    - `times_shown_lower_bound` and `times_shown_upper_bound`.
    - `times_shown_availability_date`, filled when no impressions are published yet.
  - `audience_selection_approach_info`: `demographic_info`, `geo_location`, `contextual_signals`, `customer_lists` and `topics_of_interest`, each `CRITERIA_INCLUDED`, `CRITERIA_EXCLUDED`, `CRITERIA_INCLUDED_AND_EXCLUDED` or `CRITERIA_UNUSED`.
  - Also `topic`, `is_funded_by_google_ad_grants` and `ad_funded_by`.
- `removed_creative_stats` adds `disapproval` (`removal_reason`, `violation_category`, `use_of_automated_means`, `removal_location`, `decision_type`) — [README](https://storage.googleapis.com/ads-transparency-center/api-data/README.txt)
- BigQuery on-demand pricing is $6.25 per TiB, with the first 1 TiB per month free — [BigQuery pricing](https://cloud.google.com/bigquery/pricing)

#### What the export looks like today [live check]
- **Bucket layout**, from the public Cloud Storage JSON API — [bucket listing](https://storage.googleapis.com/storage/v1/b/ads-transparency-center/o?prefix=api-data/):
  - `api-data/creative-stats/` holds 5,000 objects (671 GB).
  - 2,500 shards (427.9 GB) were rewritten on 2026-10-22 at 09:44 UTC. The other 2,500 (`data-000000002500` onward, 243.5 GB) are stale, last written 2025-10-15.
  - `removed_creative_stats` holds 1,000 shards (34 GB), rewritten 2026-10-22.
- **One current shard**, `data-000000000007.json` (170 MB) — [shard](https://storage.googleapis.com/ads-transparency-center/api-data/creative-stats/data-000000000007.json):
  - 65,050 creatives, so the export holds about 160 million (extrapolation).
  - Formats: TEXT 65%, IMAGE 23%, VIDEO 11%. 97% of creatives are `VERIFIED`.
  - Most common `advertiser_location` values: DE, NL, US, PL, LU, FR.
  - Regions: the `EEA` aggregate plus 37 country codes; FR appears on 19% of creatives.
  - `surface_serving_stats`, which the README does not mention, gives lower and upper bounds per surface: `SEARCH`, `YOUTUBE`, `SHOPPING`, `MAPS`, `PLAY`.
- **`topic` is a vertical taxonomy** with 56 values in that shard, so it can serve as the category. The largest:
  - Travel & Tourism 14,615; Business & Industrial 7,833; Apparel 5,484; Home & Garden 4,931; Hobbies, Games & Leisure 3,878.
  - Autos & Vehicles 2,818; Computers & Consumer Electronics 2,529; Beauty & Personal Care 2,215; Health 2,199; Finance 1,104; Real Estate 1,119.
  - It mixes two schemes, for example "Apparel" and "Apparel & Accessories". "Political" has 3 creatives.
  - Source: [shard](https://storage.googleapis.com/ads-transparency-center/api-data/creative-stats/data-000000000007.json)
- **Freshness** — [shard](https://storage.googleapis.com/ads-transparency-center/api-data/creative-stats/data-000000000007.json):
  - The latest `last_shown` is 2026-10-21, a one-day lag.
  - The latest `times_shown_end_date` is 2026-07-23, about 91 days back.
  - Every region entry without impressions carries `times_shown_availability_date` = `first_shown` + 90 days. For example, first shown 2026-10-13 gives 2027-01-11, and 2026-07-29 gives 2026-10-27.
  - 18,194 of 207,050 region entries (8.8%) had no impression figures yet; for FR, 1,056 of 12,424 (8.5%).
- **Impression bounds come in buckets.** In that shard, 68% of FR entries are 0–1,000. Buckets then step by 1,000 up to 10,000, by 5,000 (10k–15k…), by 10,000 (50k–60k…), by 25,000 (100k–125k…), then by 50,000 (250k–300k…) — [shard](https://storage.googleapis.com/ads-transparency-center/api-data/creative-stats/data-000000000007.json)
- **Agencies as advertisers.** In that one shard, the advertisers with the most FR creatives first shown since 2026-09-22 included agency and reseller entities (e.g. "HAVAS Business Science", "MIGHTYHIVE LTD") next to brands — [shard](https://storage.googleapis.com/ads-transparency-center/api-data/creative-stats/data-000000000007.json)
- **Query cost estimate.** Applying BigQuery's data-size rules to the sample shard:
  - a query reading `advertiser_id`, `advertiser_disclosed_name`, `topic`, `creative_id` and the `region_stats` code, dates and bounds scans about 33 GB;
  - reading `surface_serving_stats` adds about 49 GB.
  - Both are estimates: the real column types in BigQuery were not checked.

#### Other sources on the same data
- A 2026 vendor guide agrees on several points — [AdMakeAI, 2026-07-05](https://admakeai.com/blog/google-ads-transparency-center) [vendor]:
  - EU impression data runs "since March 1, 2023" and publishes "after a 90-day delay for privacy reasons";
  - the BigQuery dataset is "the only bulk programmatic access to commercial ad data Google offers at all";
  - "no official API or bulk export for commercial ads outside the EEA".
- One user's BigQuery query returned 3 creatives for an advertiser while the website showed about 200. The answer: the table holds only "the European Economic Area or Turkey". Time-travel queries were denied — [Google Developer forum, 2025-01-03](https://discuss.google.dev/t/querying-public-google-ads-transparency-center-table-doesnt-show-all-the-needed-data/177804)
- Another user reports duplicated rows in an extract — [forum, 2025-03-30](https://discuss.google.dev/t/bq-dataset-google-ads-transparency-center/185395)
- The website shows ads "within 48-72 hours after the ad is shown", and non-political ads are "tracked for 365 days" — [PPC Land, 2024-04-01](https://ppc.land/a-deep-dive-into-the-google-ads-transparency-center/) (older, may have changed)
- Around 28 Sept 2025, about seven years of EU political-ad history were removed from the Transparency Center and the separate `google_political_ads` BigQuery dataset — [AdMakeAI](https://admakeai.com/blog/google-ads-transparency-center) [vendor]; [Hacker News thread](https://news.ycombinator.com/item?id=45411332)

#### Paid APIs that reach the website, including the US
- SearchAPI `google_ads_transparency_center` — [SearchAPI docs](https://www.searchapi.io/docs/google-ads-transparency-center-api):
  - inputs: `advertiser_id` or `domain`, `region` (default `anywhere`), `platform` (`google_search`, `youtube`, `google_shopping`, `google_play`, `google_maps`), `ad_format`, `time_period` (`last_7_days`, `last_30_days` or a custom range), `num` (max 100) and `next_page_token`;
  - per creative it returns `first_shown_datetime`, `last_shown_datetime`, `total_days_shown`, `format`, `target_domain`, the advertiser's ID and name, and `details_link`.
- SearchAPI `google_ads_transparency_center_ad_details` — [SearchAPI ad details docs](https://www.searchapi.io/docs/google-ads-transparency-center-ad-details-api):
  - adds `topic`, plus per-region first and last shown dates;
  - adds `impressions` lower and upper bounds, `platform_impressions` and `audience_selection`;
  - the example shows impression bounds for DE.
- SerpApi's equivalent has 250 free searches a month, then $25 per 1,000 searches, with no impressions and no spend ([SerpApi](https://serpapi.com/google-ads-transparency-center-api), via the helper file)
- Traps from the founder's v1 runs [local note]:
  - `total_results` caps at 200 per region, so 200 is a floor. This conflicts with SearchAPI's documented example showing 4,000.
  - The `domain` filter returns affiliates and resellers under their own legal entities; first-party share ranged from 20% to 100% in one study.
  - Text creatives carry a rendered PNG.
  - Video creatives resolve to YouTube IDs through `details_script_link` (194 of 232).

### Inferences
- **Impression growth over the last 30 or 90 days cannot be ranked from one snapshot.** Impressions are cumulative bounds frozen 90 days back. Two signals work instead:
  - **Fresh (one-day lag):** new creatives per advertiser in FR in the last 28 days against the previous 28; active creatives (`last_shown` within 7 days); new entrants (earliest FR `first_shown` within 60 days).
  - **Lagged:** store the cumulative bounds per (creative, FR) every week. The week-over-week difference is the impressions served in a week about 13 weeks earlier, which gives a real but stale impression-growth series per advertiser and per topic.
- **Example SQL (BigQuery)**, written against the verified schema. `SAFE_CAST` covers bounds stored as STRING or INT64, which was not checked:

```sql
-- Rising advertisers in France: fresh creative velocity plus lagged impressions, top 20 per topic
DECLARE today DATE DEFAULT CURRENT_DATE();
WITH fr AS (
  SELECT c.advertiser_id, c.advertiser_disclosed_name AS advertiser, c.advertiser_location,
         c.topic, c.creative_id, r.first_shown, r.last_shown,
         SAFE_CAST(r.times_shown_lower_bound AS INT64) AS imp_lo,
         SAFE_CAST(r.times_shown_upper_bound AS INT64) AS imp_hi
  FROM `bigquery-public-data.google_ads_transparency_center.creative_stats` AS c,
       UNNEST(c.region_stats) AS r
  WHERE r.region_code = 'FR'
),
per_adv AS (
  SELECT advertiser_id,
         ANY_VALUE(advertiser) AS advertiser,
         ANY_VALUE(advertiser_location) AS advertiser_location,
         APPROX_TOP_COUNT(topic, 1)[OFFSET(0)].value AS main_topic,
         MIN(first_shown) AS first_seen_fr,                                  -- clipped at 2023-03-01
         COUNTIF(first_shown > DATE_SUB(today, INTERVAL 28 DAY)) AS new_28d,
         COUNTIF(first_shown > DATE_SUB(today, INTERVAL 56 DAY)
                 AND first_shown <= DATE_SUB(today, INTERVAL 28 DAY)) AS new_prev_28d,
         COUNTIF(last_shown > DATE_SUB(today, INTERVAL 7 DAY)) AS active_7d,
         SUM((imp_lo + imp_hi) / 2) AS fr_impressions_mid_lagged             -- cumulative, ~90 days old
  FROM fr
  GROUP BY advertiser_id
)
SELECT *, SAFE_DIVIDE(new_28d, new_prev_28d + 1) AS velocity_ratio,
       first_seen_fr > DATE_SUB(today, INTERVAL 60 DAY) AS new_entrant
FROM per_adv
WHERE new_28d >= 10
QUALIFY ROW_NUMBER() OVER (PARTITION BY main_topic ORDER BY new_28d DESC) <= 20
ORDER BY main_topic, new_28d DESC;
```

- **Weekly lagged-impressions job:** insert `(snapshot_date, advertiser_id, creative_id, topic, times_shown_end_date, lower, upper)` for `region_code = 'FR' AND times_shown_end_date IS NOT NULL` into a table of your own, or export it to Parquet. Then aggregate per advertiser the difference of the bound midpoints between consecutive snapshots of the same creative.
- **Map advertisers to brands before ranking.** The dataset has no landing domain, and advertisers include agencies and resellers. Resolve the domain from the creative page or from SearchAPI's ad-details `variations`. Use `advertiser_location = 'FR'` to keep French-registered advertisers.
- **Download only the current export.** A naive download of the folder would mix in the 2,500 shards left from 2025-10-15. List the bucket and keep the objects updated on the latest date, or query BigQuery instead.

### Gaps
- The Additional Terms page (adstransparency.google.com/terms) did not render, so licence and reuse limits are unverified.
- I used no GCP credentials. The BigQuery table's own last-modified time and column types are unverified; the daily refresh is inferred from the Cloud Storage export.
- The 90-day impression lag is consistent across all three sources (README, vendor guide, live data), but Google's exact rule was not read in its own words.
- Unknown whether creatives drop out one year after `last_shown`. If they do, an advertiser that returns after a year away looks new.

## 3. TikTok: Commercial Content API, the web Ad Library, Creative Center

### Takeaway
TikTok's official **Commercial Content API (CCAPI)** is free after an application. It covers 32 European countries, not the US. **Its terms may rule out commercial use.** TikTok's Research Tools Terms of Service (effective 22 Jan 2026) forbid commercial use and sharing derived data, and secondary guides say businesses are not eligible. Whether those terms govern the CCAPI is unverified.
- **Ad query:** search by keyword, country, date and reach band.
- **Ad details:** unique users seen per region × age × gender, full targeting, landing URL, objective, and the advertiser's business ID.
- **Ad report:** a **daily time series of ad counts per country for given advertisers** (`count_time_series_by_country`), the most direct official "rising advertiser" series on any platform.

The Creative Center (Top Ads, Top Products) covers the US and France, but it shows opt-in, curated "top" ads and product popularity, not who is spending. Treat it as a trend signal, not a measurement.

### Cited Findings
- **Who and where [doc]** — [TikTok CCAPI product page](https://developers.tiktok.com/products/commercial-content-api):
  - the API serves "the public and researchers"; you sign up with an "official email address", fill a form, and "should hear back from us within 2 working days";
  - "in this phase we are ONLY including data from EU countries";
  - ad data stays accessible while the ad runs and "until one year since the advertisement was last shown to any user".
- **Supported countries:** 32 — the 27 EU states, plus IS, LI and NO, plus GB and CH. No US. The page is dated 2026-09-01 — [Supported countries](https://developers.tiktok.com/doc/commercial-content-api-supported-countries) [doc]
- **Onboarding [doc]** — [CCAPI getting started, updated 2026-08-27](https://developers.tiktok.com/doc/commercial-content-api-getting-started):
  - access is framed as a research project: "Once your application is approved, a research client will be generated for your project", whose client key and secret appear under `developers.tiktok.com/research/`;
  - you generate a client access token and send it as a bearer token;
  - the page's footer links the [TikTok Developer Terms of Service](https://www.tiktok.com/legal/page/global/tik-tok-developer-terms-of-service/en);
  - the page states no rate limits and no usage restrictions.
- **TikTok Research Tools Terms of Service**, effective 22 Jan 2026, read by the helper — [TikTok Research Tools ToS](https://www.tiktok.com/legal/page/global/terms-of-service-research-api/en):
  - **eligibility:** "academic research institutions and other non-academic research bodies, organizations and associations" whose principal aims include "research on a not-for-profit basis", or anyone TikTok otherwise grants access;
  - **commercial use:** forbids use "for any commercial or unauthorized purpose";
  - **refresh:** "refresh TikTok Research Data at least every thirty (30) days" and delete data no longer available;
  - **sharing:** no disclosure, sale or transfer of "any TikTok Research Data", including "any data derived or aggregated from" it;
  - **publication:** TikTok gets a copy 7 days before publication.
  - The text never names the Commercial Content API, so whether it applies there is unverified.
- Secondary guides say businesses are not eligible for the CCAPI — [dev.to guide](https://dev.to/odeeb/the-tiktok-ad-library-api-a-developers-honest-guide-to-the-dsa-commercial-content-library-5446); [adlibrary.com](https://adlibrary.com/guides/tiktok-ad-library-api) [vendor, snippet].
- **Ad query [doc]** — [Query ads](https://developers.tiktok.com/doc/commercial-content-api-query-ads):
  - `POST https://open.tiktokapis.com/v2/research/adlib/ad/query/`, scope `research.adlib.basic`;
  - filters: `ad_published_date_range` (required; `min` within one year), `country_code_list`, `ad_type`, `ad_status`, `ad_reach` (`0-10K`, `10K-100K`, `100K+`), `ages`, `gender`;
  - `search_term` up to 50 characters, `search_type` exact or fuzzy phrase;
  - **`max_count` is at most 10 per request**; paging uses `search_id` and `has_more`;
  - the page itself has inconsistencies, for example `unique_user_seen` against `unique_users_seen`.
- **Ad details [doc]** — [Ad details](https://developers.tiktok.com/doc/commercial-content-api-get-ad-details):
  - `POST /v2/research/adlib/ad/detail/`;
  - reach: `reach.unique_users_seen` (abbreviated strings such as "30K"), and `unique_users_seen_breakdowns` by region × age × gender;
  - `targeting_info`: `number_of_users_targeted`, `country`, `age`, `gender`, `interest`, `video_interactions`, `creator_interactions`, `audience_targeting`, `high_spending_power`, provinces, cities, languages, devices;
  - ad: `external_url`, `advertising_objective`, `call_to_action`;
  - advertiser: `business_id`, `business_name`, `country_code`, `paid_by`, `follower_count`.
- **Ad report [doc]** — [Ad report](https://developers.tiktok.com/doc/commercial-content-api-get-ad-report):
  - `POST /v2/research/adlib/ad/report/?fields=count_time_series_by_country`;
  - filters: `ad_published_date_range`, `country_code` (default ALL), `advertiser_business_ids`;
  - returns, per country, a list of `{date, count}` ("total ads for that day");
  - the earliest allowed `min` is after 1 Oct 2022.
- **Rate limits** are not published for CCAPI.
  - TikTok's separate Research API is cited at 1,000 requests and 100,000 records a day — [Phyllo, 2026-07-01](https://www.getphyllo.com/post/tiktok-api-rate-limits-in-2026-quotas-errors-workarounds) [vendor, snippet].
  - An academic audit finds the Meta and TikTok research APIs inadequate for systemic-risk audits, with request limits down to about 1,000 a day — [arXiv 2601.12390](https://arxiv.org/html/2601.12390v1) [snippet].
- **Regulatory track record:**
  - 15 May 2025: the Commission found preliminarily that TikTok's ad repository breached the DSA — [Euronews](https://euronews.com/next/2025/05/15/tiktoks-ad-database-breaches-eu-platform-rules-says-commission).
  - 5 Dec 2025: the Commission accepted "binding commitments", which I re-read on the Commission page — [Commission press release](https://digital-strategy.ec.europa.eu/en/news/commission-accepts-tiktoks-commitments-advertising-transparency-under-digital-services-act):
    - the full ad as shown, "including the URLs";
    - repository data available "within a maximum of 24 hours";
    - the "targeting criteria selected by advertisers";
    - aggregated reached-user data by "gender, age group and Member State";
    - "additional search options and filters".
  - Per search summaries, implementation deadlines run 2–12 months [snippet].
  - An Austrian institute's audit found that, as of April 2026, "none of these points had been implemented" — [ÖIAT policy brief, May 2026](https://research.oiat.at/fileadmin/Research/Dokumente/PolicyBrief_AdWatch_AdLibraries_EN.pdf).
  - The commitments run for five years — [MLex via search](https://www.mlex.com/mlex/articles/2452658) [snippet].
- Mozilla and CheckFirst, testing in Dec 2023–Jan 2024: "TikTok: The ad repository and API look robust, but we encountered gaps and accuracy errors" — [Full Disclosure report](https://assets.mofoprod.net/network/documents/Full_Disclosure_Stress_Testing_Tech_Platforms_Ad_Repositories_3FepU2u.pdf)
- **SearchAPI `tiktok_ads_library`** — [SearchAPI docs](https://www.searchapi.io/docs/tiktok-ads-library-api):
  - inputs: `q`, `advertiser_token` (`advertiser_id` alone is no longer supported), `country`, `time_period` (default: the past year), `sort_by` (including `unique_users_seen_high_to_low` and `published_date_newest_to_oldest`);
  - returns `first_shown_datetime`, `last_shown_datetime`, `estimated_audience` with min and max, `advertiser_id` and `rejection_info`;
  - `total_results` was 5,000 in the examples, possibly a cap.
- **Unofficial web endpoints** [local note; undocumented; terms-of-service risk]:
  - `library.tiktok.com/api/v1/reports` returns `ad_published.rows` (ads published per day) per advertiser and region, and was "never throttled". An empty advertiser ID returns the whole library ("820 M ads for FR").
  - `/api/v1/search` throttles hard: eight searches in 15 s blocked the IP for more than 34 minutes.
  - Advertiser IDs are snowflakes: `id >> 32` is the Unix time the business account was created, which is a new-advertiser signal.
- **Creative Center:**
  - Top Ads shows ads "authorized by advertisers inside TikTok Ads Manager", with filters for region, industry and campaign objective (page updated May 2025) — [About Top Ads](https://ads.tiktok.com/help/article/top-ads?lang=en) [doc].
  - Listings show likes, a CTR percentile against the industry, and a budget tier — [Moda 2026](https://moda.app/blog/tiktok-creative-center) [snippet].
  - Top Products ranks by "Popularity" or "Popularity change", on desktop only — [TikTok help](https://ads.tiktok.com/help/article/how-to-use-top-products) [snippet].
  - Product detail shows CTR, CPA and an impressions chart — [Search Engine Land](https://searchengineland.com/leveraging-tiktoks-ad-content-to-get-valuable-insights-on-top-performing-products-393566) [snippet].

### Inferences
- **For France and the EU, the CCAPI ad report gives an advertiser-level daily series of ads published.** A weekly job can:
  1. discover advertisers with the ad query (category keywords, `country_code_list=['FR']`, last 7 days of publication, `ad_reach=['100K+']`);
  2. pull the 90-day `count_time_series_by_country` for those business IDs;
  3. add the FR `unique_users_seen` of their new ads from ad details;
  4. estimate spend as unique users × frequency × TikTok CPM, as for Meta.
- At 10 results per query call, discovery is slow. Use the ad report for the time series, and the query only to find candidates.
- Creative Center fits a weekly "what is trending in the US" scan of Top Products by category. It shows neither advertisers' spend nor who is new.

### Gaps
- No CCAPI rate limits found.
- The CCAPI docs link only the general TikTok Developer Terms of Service, which neither I nor the helper could fetch. The Research Tools terms (commercial use forbidden) were read, but they do not name the CCAPI. Whether a commercial weekly tracker may use the CCAPI is the main open question; ask TikTok (commercial-research-questions@tiktok.com) before building on it.
- Unclear whether a commercial applicant, as opposed to a researcher, is approved. The product page names "the public and researchers", the onboarding creates a "research client" for a "project", and secondary guides say businesses are not eligible.
- The official Creative Center pages define no metrics, and nothing documents that its "budget" tiers reflect real spend.

## 4. LinkedIn, Microsoft (Bing), Snapchat, Pinterest, Reddit, and briefly Apple, X and Amazon

### Takeaway
None of these libraries publishes spend for commercial ads; only political-ad libraries (Snapchat's CSV, Reddit's subreddit) carry money figures. For rising EU advertisers, three are the most useful:
- **Snapchat:** exact impression counts per ad and per EU country, through a keyless API.
- **Microsoft (Bing):** an impression band and a per-country share, through a public API that can list every ad by country and date.
- **LinkedIn:** estimated impressions and country percentages, for EU-targeted ads only. Its API is gated.

Pinterest publishes EU reach in 10K bands with no API found. Reddit was designated a very large platform under the DSA only on 31 Aug 2026, so its library is not live yet. None of these libraries covers US delivery with dates or reach.

### Cited Findings
Facts in this section were verified by a helper agent on 2026-10-22, including keyless test calls marked [live check, helper].
- **LinkedIn Ad Library**:
  - **Coverage:** all ads shown after 1 June 2023, kept one year after the last impression; filters for advertiser, payer, keyword, country and date range — [LinkedIn help a1517918](https://www.linkedin.com/help/linkedin/answer/a1517918).
  - **EU-targeted ads only:** "estimated total impressions", country shares "rounded to the nearest percent", and targeting across 12 categories flagged as inclusion or exclusion — [LinkedIn help a1620070](https://www.linkedin.com/help/linkedin/answer/a1620070).
  - **Impression format:** a scraper's output shows bands such as "1k-5k" plus first and last shown dates for EU ads — [Apify](https://apify.com/jmlp/linkedin-ad-library-scraper.md) [third party].
  - **API:**
    - The "Ad Library API" page (`linkedin.com/ad-library/api`) returned 403.
    - A GitHub issue opened 2024-09-29 shows `GET https://api.linkedin.com/rest/adLibrary?q=criteria&keyword=…&advertiser=…` with a bearer token and `Linkedin-Version 202408` — [issue #64](https://github.com/linkedin-developers/linkedin-api-python-client/issues/64).
    - Access is a gated, free product you request on the developer portal — [zenabm, 2026-06-29](https://zenabm.com/blog/linkedin-ads-library-api) [vendor].
  - **v1 observation** [local note]: an ad detail page with no impressions block means a US-only campaign, a free geography split.
  - **SearchAPI `linkedin_ad_library`** — [SearchAPI docs](https://www.searchapi.io/docs/linkedin-ad-library-api):
    - inputs: `q`, fuzzy `advertiser`, `advertiser_id` (up to 1,000 company IDs), multi-value `country`, `time_period` (`last_30_days`, `this_month` or a custom range up to a year back);
    - an Ad Details call adds run dates, estimated impressions, impressions per country and targeting.
- **Microsoft Ads Library (Bing)**:
  - Covers EEA-served ads only, "primarily intended for regulatory visibility rather than performance analysis". Impressions are recorded since June 2023, with a 1–3 day delay — [Microsoft Learn: Ad Library API, updated 2026-06-05](https://learn.microsoft.com/en-us/advertising/guides/ad-library-api).
  - **API base:** `https://adlibrary.api.bingads.microsoft.com/api/v1/`, with endpoints:
    - `Advertisers?searchText&top&skip`;
    - `Ads?searchText&advertiserId&countryCodes&startDate&endDate&top&skip`, where countries are numeric (France = 66);
    - `Ads({AdId})`.
  - **Details fields:** `PaidForByName`, `StartDate`, `EndDate`, `TotalImpressionsRange`, `ImpressionsByCountry`, and `Targets` (including LinkedIn-profile targeting).
  - **Access:** anonymous calls get "stricter limits", with no numbers published. Higher limits need a Microsoft Advertising account, a developer token and OAuth.
  - I re-read the page myself today [doc]:
    - the library "allows you to view all ads shown on Bing.com" but "contains only advertisements served within the European Economic Area (EEA)";
    - `Ads` returns 12 items by default (`top`, `skip`);
    - `AdDetails` can only be expanded for one ad at a time;
    - `TotalImpressionsRange` counts EU and EEA impressions;
    - `ImpressionsByCountry` gives each country's share as a percentage;
    - targeting types are Gender, Age, Location, MicrosoftAudiences (including LinkedIn profile targeting) and AdvertiserAudiences (including remarketing and customer-match lists);
    - "there may be a 1-3 day delay";
    - the page dates its documentation 2025-09-05 and was updated 2026-06-05.
  - [live check, helper]:
    - listing ads for France and October dates **without any search text works**, but returned 1,000 on both queries, which looks like a cap;
    - the France filter also returned German retailers' shopping ads;
    - one French ad showed `TotalImpressionsRange "5M - 10M"` with France at 99.5%.
- **Snapchat Ads Gallery (EU)**:
  - Covers "Ads that delivered in the European Union in the last 12 months". The API (`https://adsapi.snapchat.com/v1/ads_library/`) does "not require an OAuth token". `POST /ads/search` takes `paying_advertiser_name`, `countries`, dates and status, with cursor paging — [Snap docs: Introduction](https://developers.snap.com/marketing-api/Ads-Gallery-Api/Introduction); [Using the API](https://developers.snap.com/marketing-api/Ads-Gallery-Api/using-the-api).
  - [live check, helper]:
    - with no advertiser name the call fails: HTTP 400 `E3024` "payingAdvertiserName is required";
    - the name match is loose: "a" with FR returned 10 ads from unrelated advertisers plus a next-page link;
    - fields include `impressions_total` (an **exact integer**), `impressions_map` (exact counts per EU country, plus Türkiye), `start_date`, `status`, targeting, `paying_advertiser_name` and media links;
    - no 429 in two calls. The v1 runs saw fast 429s and pacing of about 0.4 s [local note].
  - **Completeness:** an April 2026 audit found that most Snapchat ads seen in the feed were missing from its archive. The web interface searches only by exact username, while the API matches loosely (above) — [ÖIAT policy brief, May 2026](https://research.oiat.at/fileadmin/Research/Dokumente/PolicyBrief_AdWatch_AdLibraries_EN.pdf).
  - **Political ads:** one ZIP per year with spend and impressions per ad, worldwide including the US — `storage.googleapis.com/ad-manager-political-ads-dump/political/<YEAR>/PoliticalAds.zip`. The 2026 file has 10,150 rows: US 7,337, UK 705, FR 75 — [Snap political ads](https://www.snap.com/political-ads) [live check, helper].
- **Pinterest Ads Repository**:
  - Covers ads shown in the EU over the past 12 months — [Pinterest help](https://help.pinterest.com/en/node/3763) (undated).
  - Filters: display period, category, country, targeted gender and age, advertiser name.
  - Each ad shows targeting and EU reach "in 10K ranges". No payer, no per-country split, no impressions.
  - No API found (unverified).
- **Reddit**:
  - Designated a very large platform on 31 Aug 2026, with duties applying "by January 2027" — [Commission list of VLOPs/VLOSEs](https://digital-strategy.ec.europa.eu/en/policies/list-designated-vlops-and-vloses); [Commission press release](https://digital-strategy.ec.europa.eu/en/news/commission-designates-chatgpt-reddit-roblox-under-digital-services-act). No DSA ad library found live (unverified: reddit.com blocks automated tools).
  - Political ads are disclosed in r/RedditPoliticalAds, with spend, impressions and dates, US federal races only — [TechCrunch 2020](https://techcrunch.com/2020/04/13/reddit-announces-updates-including-a-new-subreddit-to-increase-political-ad-transparency).
- **Apple App Store ad repository** (EU):
  - Official API, needing no auth — [Apple Ad Repository PDF v1.0, March 2025](https://developer.apple.com/support/downloads/Ad-Repository.pdf):
    - lists ads per country, app or developer for the last 90 days, 180 days or year;
    - fields: placement, format, targeting yes/no flags, first and last impression dates;
    - data is 7 days behind;
    - no reach figures.
  - [live check, helper] France alone returned 150,509 ads for 19 Jul–17 Oct 2026.
- **X:**
  - A CSV-based repository — [X help](https://business.x.com/en/help/ads-policies/product-policies/ads-transparency) [snippet].
  - On 5 Dec 2025 the Commission fined X €120M, partly because its ad repository lacks content, topic and payer, has access barriers and "excessive delays", and because X's terms bar independent access including scraping — [Commission](https://digital-strategy.ec.europa.eu/en/news/commission-fines-x-eu120-million-under-digital-services-act).
- **Amazon:**
  - A library covering "all ads and affiliate marketing content shown on the Amazon EU Store" for the past year — [Amazon DSA page, updated 2026-08-31](https://trustworthyshopping.aboutamazon.com/resources/digital-services-act-dsa). Fields are unverified because the page is a JavaScript app.
  - An "Ad Library API" was reported at `advertising-api-eu.amazon.com` in 2024 — [Mozilla/CheckFirst report](https://assets.mofoprod.net/network/documents/Full_Disclosure_Stress_Testing_Tech_Platforms_Ad_Repositories_3FepU2u.pdf).

### Inferences
- **Snapchat is the only free, keyless source of exact per-country impression counts** for commercial ads in the EU. Sweep it weekly with short substrings of advertiser names, store `impressions_map.fr`, and difference the weeks. That gives an exact (EU-only) impression-growth series per paying advertiser.
- **Microsoft is the only official API that lists every ad in a country and date window without a keyword.** Slice the dates per day to stay under the apparent 1,000 cap. The impression bands are coarse, for example 5M–10M.
- **LinkedIn matters only for B2B ideas.** Its EU impressions are estimated bands, and its API is gated.

### Gaps
- LinkedIn API eligibility, quotas and terms; LinkedIn's exact band format.
- Snapchat and Microsoft rate-limit numbers; Snap API terms.
- Pinterest API; Amazon fields; Reddit's DSA library; whether r/RedditPoliticalAds is still updated.
- The scraping terms of LinkedIn, Pinterest and Amazon were not re-read today.

## 5. Third-party ad intelligence (spend or impression estimates): what each estimates, coverage, price, API

### Takeaway
Tools that model spend from panels or CPMs start at about $129/month (AdClarity Basic: one market, one channel) and climb to enterprise contracts: Sensor Tower/Pathmatics, MediaRadar/Vivvix around $25k a year, Similarweb Ads around $542/month. Under €100/month the options split three ways:
- **Search spend models:** SpyFu ($39–119) and Semrush Advertising Base (€94.94/month billed yearly), which are Google-Search-only and were off by roughly 2–3× in a single-account test.
- **EU-reach products built on Meta's DSA data:** Trendtrack, about $34–111 billed yearly.
- **Creative "spy" tools:** BigSpy, Foreplay, Minea, PiPiAds, Gethookd and others, which show creatives, days running and live-ad counts but no spend.

For this goal the platforms' own EU data, plus SearchAPI and SE Ranking, beat these tools on cost. The full table is in `ad_intel_tools_pricing.md`.

### Cited Findings
All points come from the helper file `ad_intel_tools_pricing.md` (pages read 2026-10-22), with the helper's sources:
- **Semrush Advertising:**
  - toolkit Base €94.94/month, Pro €210.98/month, billed yearly; only Pro adds AdClarity — [Semrush pricing](https://www.semrush.com/pricing/advertising/);
  - France is one of the nine core markets, with history from 2012 — [Semrush KB 64](https://www.semrush.com/kb/64-historical-data);
  - the API costs extra: Domain Ad History is 100 units per line, last 12 months — [Semrush API docs](https://developer.semrush.com/api/v3/seo/domain-reports/);
  - one test estimated about $5k/month against $13.8k actual — [Jumpfly](https://www.jumpfly.com/blog/are-competitive-spying-tools-worth-it-for-ppc/) (undated).
- **Similarweb:**
  - PPC spend = paid-search visits × paid keywords × CPC, only above 5,000 paid visits — [Similarweb support](https://support.similarweb.com/hc/en-us/articles/360018815797-PPC-Spend);
  - Ads tier about $649/month ($542 billed yearly) — [PricingSaaS snapshot 2026-09-28](https://pricingsaas.com/companies/similarweb).
- **SpyFu:**
  - Google Search only, 32 countries including France and the US — [SpyFu help, 2026-03-19](https://help.spyfu.com/en/articles/2968557-which-countries-does-spyfu-collect-data-in);
  - $39–119/month per third parties; historical data only on the upper tiers — [SpyFu help](https://help.spyfu.com/en/articles/5569689-more-answers-about-our-pricing-and-plans);
  - estimated about $6k/month against $13.8k actual in the same test — [Jumpfly](https://www.jumpfly.com/blog/are-competitive-spying-tools-worth-it-for-ppc/).
- **Sensor Tower Ad Intelligence (ex-Pathmatics):**
  - spend, impressions and share of voice across Meta, YouTube, TikTok, X, Snapchat, LinkedIn, display and CTV, but not search; markets include FR and US; price on demo only — [Sensor Tower](https://sensortower.com/pathmatics-connect).
- **MediaRadar (+Vivvix):**
  - merger announced 2023-11-02 — [Kantar](https://www.kantar.com/north-america/company-news/mediaradar-acquires-vivvix-kantars-north-american-ad-intelligence-business);
  - about $19k–97k a year, median about $25k — [Vendr](https://www.vendr.com/marketplace/mediaradar).
- **Adbeat:** display and native; Standard $249/month, Advanced $399; spend estimates on Enterprise only — [Adbeat pricing](https://www.adbeat.com/pricing).
- **AdClarity:** Basic $129/month (one market, one channel, three months); panel based — [AdClarity pricing](https://www.adclarity.com/pricing/).
- **Creative spy tools, none estimating spend:**
  - BigSpy: free tier, $49–499 — [BigSpy](https://bigspy.com/pricing);
  - AdSpy: $149 — [AdSpy](https://adspy.com/);
  - PowerAdSpy: $27–399, with an "Estimated Ad Budget" of unpublished method — [PowerAdSpy](https://poweradspy.com/pricing/);
  - Foreplay: $49–459, API from $175 — [Foreplay](https://www.foreplay.co/pricing);
  - Minea: $49–199 — [Minea](https://www.minea.com/pricing);
  - PiPiAds: $49–99 — [PiPiAds](https://www.pipiads.com/pricing) [snippet];
  - Atria: $129, REST API 1,200 calls a month — [Atria](https://www.tryatria.com/pricing);
  - Gethookd: $19–129; "We do not estimate a brand's revenue or invent a spend figure" — [Gethookd](https://www.gethookd.ai/).
- **API-first and EU-specific:**
  - Trendtrack: about $34/62/111 a month billed yearly; EU reach and spend estimates from Meta's DSA data; API from Pro — [Trendtrack](https://www.trendtrack.io/pricing);
  - Apify Facebook Ads Scraper: $3.40–5.80 per 1,000 ads, with EU reach, age-gender-country, payer and beneficiary per ad — [Apify](https://apify.com/apify/facebook-ads-scraper);
  - ScrapeCreators: $47 for 25k credits — [ScrapeCreators](https://scrapecreators.com/);
  - Adyntel: $44 for 5k credits — [Adyntel](https://adyntel.com/);
  - Kalodata and FastMoss: TikTok Shop GMV estimates at about $45–90 — [Hubfluence, Oct 2026](https://www.hubfluence.io/blog/kalodata-vs-fastmoss).

### Inferences
- **No cheap tool estimates spend reliably.** The two search-spend tools under budget undershot one real account by 2–3×.
- **Their value is history,** which Semrush and SpyFu hold back to 2012 and 2006. The platform data starts in 2023 (EU) and lasts a year.
- **For a weekly "new top spenders" list,** the platform data, snapshotted weekly, is both cheaper and closer to the source.

### Gaps
- SpyFu and PiPiAds prices were not read on the vendors' own pages (403 and JavaScript).
- No independent accuracy audit of any spend estimator, beyond a single-account blog test, was found.

## 6. SearchAPI.io and SE Ranking (keys already held): what they return, and whether they support a time series

### Takeaway
**SearchAPI** is a live scraper of the web libraries (Meta, Google Transparency, TikTok, LinkedIn) at roughly $3–4 per 1,000 calls. It keeps no history: each call is a snapshot. A time series exists only if you store weekly snapshots. The per-ad start and first/last-shown dates do let you rebuild timelines for ads still listed. It is the only route to **US** Meta and Google creative data short of building a scraper.

**SE Ranking** (Google Search only) does hold history: monthly retro data per domain. It returns:
- paid keywords count, estimated paid traffic and its cost, new and lost paid keywords;
- the list of domains that advertised on a keyword per month, with monthly ad snippets.

So it supports a **monthly** "who started bidding in this category" series for France and the US, at 100 credits per call.

### Cited Findings
- **SearchAPI pricing**, monthly — [SearchAPI pricing](https://www.searchapi.io/pricing):
  - Developer: $40 for 10,000 searches;
  - Production: $100 for 35,000;
  - BigData: $250 for 100,000;
  - Scale: $500 for 250,000;
  - Octo tiers up to $5,000 for 5M;
  - "you can utilize only up to 20% of your plan's credits each hour"; 100 free requests; failed requests are not billed.
- **SearchAPI `meta_ad_library`** — [SearchAPI Meta docs](https://www.searchapi.io/docs/meta-ad-library-api):
  - inputs: `q`, `page_id`, `location_id`, `country` (default ALL), `content_languages`, `ad_type`, `active_status`, `search_type`, `media_type`, `platforms`, `start_date` and `end_date`, `sort_by` (`impressions_high_to_low` by default, or `most_recent`), `next_page_token` (token pages grow to 8KB+, so switch to POST);
  - per ad: `ad_archive_id`, `page_id`, `page_name`, `is_active`, `start_date`, `end_date`, `total_active_time`, `publisher_platform`, `collation_id`, `collation_count`, `targeted_or_reached_countries`, `impressions_with_index`, and the snapshot (`link_url`, `cta_type`, `display_format` such as DCO, DPA or CAROUSEL, `page_categories`, `page_like_count`, cards, images, videos);
  - with `page_id` it adds `ad_library_page_info` and a page block that includes `ad_library_page_targeting_summary` (`total_num_ads`, `total_spend_formatted`, `is_30_day_available`, `is_90_day_available`); the docs do not say whether this is political spend.
- **SearchAPI Google Transparency, TikTok and LinkedIn engines:** see sections 2–4 — [GATC](https://www.searchapi.io/docs/google-ads-transparency-center-api), [GATC ad details](https://www.searchapi.io/docs/google-ads-transparency-center-ad-details-api), [TikTok](https://www.searchapi.io/docs/tiktok-ads-library-api), [LinkedIn](https://www.searchapi.io/docs/linkedin-ad-library-api).
- **SearchAPI operations** [local note]:
  - a shared 100,000-credit plan was exhausted twice, the second time within twelve days of the 2026-10-05 renewal;
  - exhaustion answers HTTP 429 "You have used all of the searches for the month" on every engine, indistinguishable from a rate limit unless you read the body;
  - check `GET /api/v1/me` → `account.remaining_credits` first;
  - engine names: `tiktok_ads_library` (not `tiktok_ad_library`); `facebook_ad_library` and `snapchat_ad_library` do not exist.
- **SE Ranking Data API**:
  - base `https://api.seranking.com` (`/v1/...`); the older host `api4.seranking.com/research/{cc}/...` is used by the founder's tooling;
  - auth header `Authorization: Token …`;
  - every Domain Analysis call costs 100 credits; only 2xx calls are billed — [SE Ranking getting started](https://seranking.com/api/data/getting-started/); [credits system](https://seranking.com/api/api-credits-system/).
- **SE Ranking Domain Analysis endpoints** — [Domain Analysis docs](https://seranking.com/api/data/domain-analysis/):
  - `GET /v1/domain/overview/history?type=adv`: monthly entries of `keywords_count` (paid keywords), `traffic_sum` (estimated clicks), `price_sum` (traffic cost), `year`, `month`, and paid position buckets;
  - `GET /v1/domain/ads?domain=…&from=YYYY-MM&to=YYYY-MM`: per keyword, `ads_count`, `cpc`, `volume`, `competition`, plus `snippets` keyed by month (position, title, description, URL);
  - `GET /v1/domain/ads?keyword=…`: **the domains that advertised on that keyword**, with `ads_count`, `keywords_count`, `traffic_sum`, `price_sum` and monthly snippets;
  - `GET /v1/domain/competitors?type=adv`: at most 500;
  - the docs say "Data refreshes monthly".
- Monthly traffic records go back to February 2020 — [SE Ranking traffic API page](https://seranking.com/website-traffic-api.html) [snippet].
- A Data API key is capped at 10 requests per second — [SE Ranking API via search](https://seranking.com/api-pricing.html) [snippet].
- **Real captures, 2026-10-21** (the founder's fixtures, `tools/factory/fixtures/seranking/`):
  - `/research/us/overview/` returns an `adv` block for the current month: `keywords_count`, `keywords_new_count`, `keywords_lost_count`, `traffic_sum`, `price_sum`;
  - `/research/us/advertising/` returns keyword rows whose `snippets` are keyed by month (2026-06 … 2026-09) — [fixtures README](https://github.com/vladzloteanu/meikit_ai/blob/main/tools/factory/fixtures/README.md) (private repository; local path `tools/factory/fixtures/README.md`).
- **SE Ranking pricing conflicts across its own pages:** standalone Data API from $79.20 or $149 a month for 1M credits; a +$45/month add-on for 250K credits a year; enterprise from $30 per million — [SE Ranking API pricing](https://seranking.com/api-pricing.html) [snippet].

### Inferences
- **US Google Search pipeline with SE Ranking:**
  1. For about 30 seed keywords per category, call `domain/ads?keyword=…&source=us` (or `fr`) for the last 3 months, which lists who advertises.
  2. For the new domains, call `overview/history?type=adv`.
  3. Rank by month-over-month growth in `price_sum` and `keywords_count`, and by `keywords_new_count`.

  At 100 credits per call, 10 categories × 30 keywords plus 300 domains is about 60,000 credits a month.
- **SearchAPI fits weekly US sweeps of Meta and Google creatives.** One example: 200 category keywords × 2 pages × 4 weeks is about 1,600 calls a month, inside the $40 Developer plan. Keep Meta EU reach on the free official API.
- **Store every response.** Neither SearchAPI nor the libraries let you query last month's state later, and inactive ads disappear one year after their last impression.

### Gaps
- Not checked: whether SE Ranking's paid data for `fr` is as deep as for `us` (the docs' examples use us, uk and de), how far back `overview/history` goes for paid data, and the meaning of SearchAPI's `total_spend_formatted`.
- SearchAPI's page size per engine is undocumented.

## 7. Scaling heuristics: ad longevity, active ads over time, new creatives per week, duplicated creatives, sudden appearance on high-CPC keywords

### Takeaway
The practitioner heuristics are widely repeated but rest almost entirely on vendors' experience:
- ads running more than 30, 60 or 90 days are "winners";
- a rising count of live ads means scaling;
- many near-identical versions mean scaling, not testing.

I found no independent study that ties ad longevity to profitability. The best quantitative evidence, Motion's 2026 benchmark of $1.29B of Meta spend, supports two weaker claims:
1. Spend is very concentrated: about 5% of creatives take 55% of spend.
2. Bigger spenders launch more creatives per week: 18.8 per week at the top tier.

Creative velocity and longevity are therefore reasonable proxies for scale, but not for profit.

### Cited Findings
- **Motion, "Creative Benchmarks 2026"** [vendor] — [Motion research](https://motionapp.com/library/research/creative-benchmarks-2026):
  - dataset: $1.29B of Meta spend, 578,750 creatives, 6,015 accounts, 1 Sep 2025–1 Jan 2026;
  - winners are creatives with spend ≥10× their account's median and ≥$500;
  - winners are about 5% of creatives and take 55% of spend, rising from 23% for Micro accounts to 64% for Enterprise ones;
  - Enterprise advertisers launch 18.8 new creatives a week;
  - results are not linked to "ROAS, revenue, or conversion".
- A search summary of the same report says close to half of launched ads get no meaningful budget — [Motion 2026 benchmarks](https://motionapp.com/events/2026-creative-strategy-bootcamp/homebase/2026-creative-benchmarks) [snippet].
- **Longevity thresholds** — [Klipio, 2026-08-15](https://klipio.io/blog/facebook-ad-longevity) [vendor]:
  - under 30 days is "not evidence"; 30–90 days is "promising"; 90+ is "almost certainly profitable";
  - the support is the author's experience only;
  - many versions plus an old start date is the "strongest possible combination".
- **Longevity caveats** — [Klipio](https://klipio.io/blog/facebook-ad-longevity):
  - retargeting ads, aimed at a pool that keeps refilling, can run a year without good results;
  - brand ads run long for awareness goals;
  - campaigns paused and relaunched around sales reset start dates;
  - start dates are per ad, not per campaign;
  - a $50/day ad and a $5,000/day ad look the same;
  - stopped ads vanish with no history.
- **Lifespan distribution** — [AdSpyder](https://adspyder.io/blog/ad-fatigue-benchmarks/) [vendor, snippet, sample method not explained]:
  - Meta ads have a median lifespan of 4 days; 22% run 30+ days and 9.4% run 90+;
  - 14+ days plus several live variations is read as "scaling".
- WinnerAdSpy calls runtime its strongest input and claims "up to 99% accuracy" without a validation method — [WinnerAdSpy](https://winneradspy.com/blogs/how-winneradspy-determines-winning-ad-creatives) [vendor, snippet].
- Adligator's band table (ad count, run length, creative output, countries, platforms → <$5K, $5K–25K or $25K+ a month) is "a heuristic, not a formula" — [Adligator](https://adligator.com/blog/estimate-competitor-facebook-ad-spend) [vendor].
- **Signals the data actually exposes:**
  - variant counts: Meta's `collation_count` ("this ad has multiple versions") and the `DCO`/`DPA` formats — [SearchAPI Meta docs](https://www.searchapi.io/docs/meta-ad-library-api);
  - new paid keywords: SE Ranking's `keywords_new_count` and monthly `price_sum` — [SE Ranking Domain Analysis](https://seranking.com/api/data/domain-analysis/);
  - newly entered keywords: Semrush's "Position Changes" — [Semrush pricing](https://www.semrush.com/pricing/advertising/).
- Only 5–8% of ads become genuine winners per Motion — [Motion search summary](https://motionapp.com/library/research/creative-benchmarks-2026) — so counts of ads overstate scale for testing-heavy advertisers.

### Inferences
- **A robust composite** for "rising" (weekly, per advertiser, per category and country):
  - growth in exposure where measured: EU reach on Meta, Snapchat impressions, TikTok unique users, Google impressions (lagged);
  - growth in creative velocity: new creatives per week against the advertiser's own 4–8-week baseline;
  - the share of active ads older than 30 days, as survivors being refunded;
  - variants per concept (`collation_count`) for Meta;
  - for search, new paid keywords and month-over-month traffic-cost growth.

  Require at least two independent signals to agree before flagging.
- **Normalise within category and country,** and exclude the top stable spenders (marketplaces, big brands). Otherwise the "rising" list is just "the biggest".
- **Meta's 2025–2026 delivery changes reward many creatives per ad set** (the "Andromeda" theme in Motion's material — [Motion](https://motionapp.com/events/how-to-configure-motion-for-andromeda) [snippet]). Creative counts are probably inflating across all advertisers, so compare each advertiser with its own history and its category, not with absolute thresholds. This is an inference and was not measured.

### Gaps
- No academic or independent validation of longevity, or of creative velocity, as a predictor of spend or profit was found. The thresholds (14, 30, 60, 90 days) are folklore.
- No evidence was found for "sudden appearance on high-CPC keywords" as a predictor of profitable scaling. The data to measure it exists (SE Ranking monthly `keywords_new_count` with CPC), but nobody seems to have published a test.

## 8. DSA Article 39 obligations, and cross-platform DSA ad-repository datasets

### Takeaway
Article 39 obliges very large platforms and search engines to publish, through a search tool and APIs, each ad's content, advertiser, payer, period shown, main targeting parameters, and total reach with a breakdown by member state, kept for one year after the ad was last shown. **It does not require spend**, which is why no EU library publishes commercial spend. Enforcement has tightened the libraries:
- X was fined €120M (Dec 2025);
- TikTok's commitments were made binding (Dec 2025).

Independent audits found every repository incomplete, in 2024 (Mozilla and CheckFirst) and again in April 2026 (ÖIAT: Meta closest to compliant, Snapchat worst). No maintained, open, cross-platform dataset of commercial ads exists. The closest are:
- an open but now access-restricted Meta archive (Lejo1), used by Sciences Po médialab;
- CheckFirst's proposed standard format;
- Mozilla's 2024 stress test.

### Cited Findings
- **Article 39(1) and (2)** — [DSA Art. 39 text](https://www.eu-digital-services-act.com/Digital_Services_Act_Article_39.html):
  - the repository sits in a dedicated section of the interface, is "searchable", supports "multicriteria queries", and is reachable "through application programming interfaces";
  - each ad stays "until one year after the advertisement was presented for the last time";
  - the repository must contain no personal data of the people who saw the ad.
  - Art. 39(2), items (a)–(g):
    - (a) content, including the product, service or brand and the subject;
    - (b) on whose behalf the ad is shown;
    - (c) who paid, if different;
    - (d) the period presented;
    - (e) whether it targeted particular groups, and the main parameters, including exclusions;
    - (f) commercial communications declared under Art. 26(2);
    - (g) total reach and, where applicable, aggregate numbers broken down by member state for the targeted groups.
  - Art. 39(3): for ads removed as illegal or against terms, items (a)–(c) are replaced by the statement-of-reasons data.
  - The article contains no spend requirement.
- **Article 40(12):** platforms must give access "without undue delay" to publicly accessible data, to researchers who meet Art. 40(8)(b)–(e), including being "independent from commercial interests", "solely for performing research" on systemic risks — [DSA Art. 40 text](https://www.eu-digital-services-act.com/Digital_Services_Act_Article_40.html). A commercial bootstrapper does not qualify.
- **The Article 40 delegated act on data access** was adopted on 2 July 2025 — [UKE (Poland)](https://uke.gov.pl/en/digitalservices/ews/the-european-commission-has-adopted-a-delegated-act-on-access-to-data-from-online-platforms-for-verified-researchers,3.html); [Arcom](https://www.arcom.fr/en/press/implementation-european-digital-services-regulation-dsrdsa-adoption-delegated-act-researchers-access-data).
- **Meta Content Library**: CASD vets the applications, and API access runs in Meta's Secure Research Environment or the SOMAR enclave (updated 2026-04-30) — [Meta Transparency Center](https://transparency.meta.com/en-gb/researchtools/meta-content-library/). The listed content types do not include ads [snippet].
- **Mozilla Foundation and CheckFirst, "Full Disclosure: Stress testing tech platforms' ad repositories"**, testing Dec 2023–Jan 2024, 12 services — [Mozilla report PDF](https://assets.mofoprod.net/network/documents/Full_Disclosure_Stress_Testing_Tech_Platforms_Ad_Repositories_3FepU2u.pdf); [Mozilla page](https://www.mozillafoundation.org/en/research/library/full-disclosure-stress-testing-tech-platforms-ad-repositories/):
  - overall: "none is a fully-functional ad repository";
  - Google: "it's been six years and we still can't search by keyword";
  - Bing: "limited data in the API";
  - Snapchat: "no API" (as of 18 March 2024);
  - Pinterest: "accuracy issues and missing data";
  - X: "only provides a CSV file";
  - on accuracy: "many cases where ads in the user interface were not located in the ad repository";
  - Google and LinkedIn "show strong reliability";
  - "Google and Meta provide data going back six years";
  - "none of the examined VLOs have both sorting and filtering options";
  - the report proposes a standardised format.
- **CheckFirst's "Standardised Digital Advertising Format (SDAF)"** (Feb 2024) is a proposed common schema across repositories — [CheckFirstHQ/DSA-Standardised-Digital-Advertising-Format](https://github.com/CheckFirstHQ/DSA-Standardised-Digital-Advertising-Format).
- **Open Meta archive (Lejo1):**
  - covers political ads plus all EU ads since 17 Aug 2023, crawled with the wildcard query;
  - per-ad JSON at `https://ad-archive.nexxxt.cloud/ad/<AD_ID>`;
  - dumps only for people verified for the Meta API;
  - Kaggle copies removed after Meta's request of 16 Oct 2024;
  - "incomplete for sure" since the rate-limit reduction.
  - Source: [Lejo1/facebook_ad_library](https://github.com/Lejo1/facebook_ad_library)
- **Sciences Po médialab** used that dump to extract French-targeted ads (repository created 2025-01-24) — [medialab/DSA-facebook-ads](https://github.com/medialab/DSA-facebook-ads).
- **An academic audit** finds that the Meta and TikTok research APIs, as they stand, do not support meaningful independent systemic-risk audits, with request limits as low as about 1,000 a day — [arXiv 2601.12390](https://arxiv.org/html/2601.12390v1) [snippet].
- **Political advertising:**
  - the TTPA (Regulation (EU) 2024/900) applied from 10 Oct 2025;
  - Meta stopped political, electoral and social-issue ads in the EU from early October 2025 — [The Register, 2025-07-25](https://www.theregister.com/2025/07/25/meta_eu_political_ads/);
  - Google had announced its stop in Nov 2024 — [PPC Land](https://ppc.land/extensive-regulation-kills-digital-political-advertising-in-eu/) [snippet].
- **Enforcement:**
  - X fined €120M on 5 Dec 2025, including for its ad repository — [Commission](https://digital-strategy.ec.europa.eu/en/news/commission-fines-x-eu120-million-under-digital-services-act);
  - TikTok's commitments accepted on 5 Dec 2025 — [Commission](https://digital-strategy.ec.europa.eu/en/news/commission-accepts-tiktoks-commitments-advertising-transparency-under-digital-services-act);
  - Reddit designated on 31 Aug 2026 — [Commission list](https://digital-strategy.ec.europa.eu/en/policies/list-designated-vlops-and-vloses).
- **More enforcement**, from the helper:
  - **X:**
    - preliminary findings on 12 Jul 2024 — [Commission representation](https://luxembourg.representation.ec.europa.eu/actualites-et-evenements/actualites/commission-sends-preliminary-findings-x-breach-digital-services-act-2024-07-12_en) [snippet];
    - after the fine, 90 working days to fix the ad repository and researcher access — [eucrim](https://eucrim.eu/news/eu-fines-x-120-million-in-first-dsa-non-compliance-decision/) [snippet];
    - X appealed to the General Court on 16 Feb 2026 — [ADF International](https://adfinternational.org/news/x-challenges-e120m-fine-under-eu-censorship-law/) [snippet].
  - **TikTok:**
    - proceedings opened 19 Feb 2024 — [Commission IP/24/926](https://ec.europa.eu/commission/presscorner/api/files/document/print/en/ip_24_926/IP_24_926_EN.pdf) [snippet];
    - preliminary findings on 15 May 2025 — [Commission](https://digital-strategy.ec.europa.eu/en/news/commission-preliminarily-finds-tiktoks-ad-repository-breach-digital-services-act) [snippet].
  - **TikTok and Meta:** preliminary findings on 24 Oct 2025 on researchers' access to public data — [Commission](https://digital-strategy.ec.europa.eu/en/news/commission-preliminarily-finds-tiktok-and-meta-breach-their-transparency-obligations-under-digital) [snippet].
  - **AliExpress:** commitments made binding on 18 Jun 2025, read by the helper — [Commission](https://digital-strategy.ec.europa.eu/en/news/commission-makes-aliexpress-commitments-under-digital-services-act-binding):
    - an up-to-date ad repository, "searchable across different parameters";
    - "An API will be provided to allow EU users to independently access and extract advertisement-related data";
    - a dedicated API for Art. 40(12) researchers;
    - five years under a monitoring trustee.
  - **Fines unrelated to ad repositories:** AliExpress €550M (20 Jul 2026) and Temu €200M (28 May 2026) both concern illegal or unsafe products — [Law Society Gazette](https://www.lawsociety.ie/gazette/top-stories/2026/july/aliexpress-handed-550-million-dsa-fine/); [Slaughter and May](https://thelens.slaughterandmay.com/post/102n15m/european-commission-fines-temu-200-million-under-the-dsa) [snippets].
  - **Meta, Google and Snapchat:** "no infringement of Article 39 DSA has been established to date" against Meta, and "no findings concerning Article 39 DSA against Google or Snapchat" — [ÖIAT policy brief, May 2026](https://research.oiat.at/fileadmin/Research/Dokumente/PolicyBrief_AdWatch_AdLibraries_EN.pdf).
- **ÖIAT, "Stress Testing Advertising Repositories"** (AdWatch project; Meta, TikTok, Google and Snapchat; 13 criteria; state as of April 2026), read by the helper — [ÖIAT policy brief](https://research.oiat.at/fileadmin/Research/Dokumente/PolicyBrief_AdWatch_AdLibraries_EN.pdf):
  - all four have a public documented API and filters, but none fully complies; Meta is closest, Snapchat worst;
  - "previously findable ads may disappear from Meta's advertising repository", and phrase search is unreliable;
  - Google can be searched only by advertiser name or URL, Snapchat (web) only by exact username;
  - reach: Meta and Snapchat give exact figures, Meta also by country, age and gender; TikTok and Google give ranges;
  - Google shows one country per query, so all-EU coverage takes 27 queries;
  - payer fields are "self-declared and can be entered freely";
  - the underlying data is not public.
- **Designated platforms as of 21 Oct 2026:** 25 VLOPs and 3 VLOSEs — [Commission list](https://digital-strategy.ec.europa.eu/en/policies/list-designated-vlops-and-vloses) (summarised by the helper):
  - Apr 2023: AliExpress, Amazon Store, App Store, Booking.com, Facebook, Google Maps, Google Play, Google Shopping, Instagram, LinkedIn, Pinterest, Snapchat, TikTok, Wikipedia, X, YouTube, Zalando; search engines Bing and Google Search;
  - Dec 2023: Pornhub, XVideos (Stripchat's designation ended in 2025);
  - 2024: Shein (Apr), Temu (May), XNXX (Jul);
  - 2026: WhatsApp (Jan); Reddit and Roblox, plus ChatGPT as a search engine (Aug).
- **Political ads and research access:**
  - Meta's announcement of 25 Jul 2025 has an addendum of 6 Oct 2025 saying EU political ads stopped — [Meta newsroom](https://about.fb.com/news/2025/07/ending-political-electoral-and-social-issue-advertising-in-the-eu/) [snippet];
  - the disappearance of Google's EU political-ads archive was noticed on 28 Sep 2025, with no statement from Google — [404 Media](https://www.404media.co/google-ad-transparency-european-union/);
  - the TTPA's EU repository provisions reportedly apply from 10 Apr 2026 — [Wikipedia](https://en.wikipedia.org/wiki/Transparency_and_Targeting_of_Political_Advertising_Regulation) [snippet];
  - the Art. 40 delegated act entered into force on 29 Oct 2025. It covers only Art. 40(4) vetted-researcher access, not 40(12), with applications through [the DSA data-access portal](https://data-access.dsa.ec.europa.eu/home) — [Commission FAQ](https://algorithmic-transparency.ec.europa.eu/news/faqs-dsa-data-access-researchers-2025-07-03_en).
- **Other projects:**
  - Sciences Po's DSA ad-repository data sprint (Jan 2025) — [Sciences Po](https://www.sciencespo.fr/institut-libre-transformations-numeriques/en/news/call-for-participation-in-the-dsa-ad-repository-data-sprint/);
  - Who Targets Me's Meta Ad Library API script — [WhoTargetsMe/Ad_Library_API](https://github.com/WhoTargetsMe/Ad_Library_API);
  - AI Forensics' study of fraudulent health ads using Meta's library — [AI Forensics](https://aiforensics.org/uploads/meta_health.pdf);
  - legal analyses: [Grisse, ZGE 2025](https://www.mohrsiebeck.com/en/article/advertising-repositories-article-39-dsa-101628zge-2025-0010) and [Wolters & Zuiderveen Borgesius, arXiv 2503.05764](https://arxiv.org/abs/2503.05764).

### Inferences
- The DSA guarantees the EU dataset's existence and its fields, including reach by member state, for every very large platform. Expect it to improve under enforcement: TikTok's 24-hour update commitment, and Reddit's library due around January 2027.
- No one sells or publishes a maintained cross-platform commercial-ads dataset. Building the weekly snapshot store is the moat and the cost, and a CheckFirst-style common schema is a sensible internal format.

### Gaps
- No empirical academic paper (arXiv, FAccT, ICWSM, IMC) auditing several DSA ad repositories was found. The ÖIAT audit's underlying data is not public.
- Not checked: whether the Commission issued Art. 39 guidelines on repository structure, and whether Google restored its EU political-ads archive.
- No NGO or university project (AlgorithmWatch, NYU Ad Observatory, Weizenbaum) was found publishing commercial-ad time series.
- The Commission page for the VLOP list was summarised by the helper; the 2026 rows deserve a spot-check.

## 9. Legal and terms-of-service constraints on scraping ad libraries and storing the data

### Takeaway
The cleanest routes are the official APIs:
- Meta, with identity confirmation;
- TikTok CCAPI, after an application, though TikTok's Research Tools terms forbid commercial use (whether they govern the CCAPI is unverified);
- Microsoft, Snapchat and Apple, which are public;
- Google's BigQuery dataset, under Google's terms plus Additional Terms.

Meta's documented stance is that bulk copies of library data should go only to verified API users. Scraping logged-out public pages won a US case against Meta (Bright Data, 2024), but EU exposure comes from GDPR (advertisers who are natural persons), the database right, and each site's terms. For an internal weekly dataset:
- prefer the APIs;
- keep only advertiser-level aggregates and the fields you need;
- do not republish raw dumps;
- treat undocumented endpoints (TikTok's web library, Meta's web library through scrapers) as revocable and terms-sensitive.

### Cited Findings
- **Meta v. Bright Data:**
  - On 23 Jan 2024, in N.D. Cal. (Judge Chen, 3:23-cv-00077-EMC), summary judgment held that Meta's terms bind only logged-in use, so logged-off scraping and sale of public Facebook and Instagram data did not breach them — [Farella Braun + Martel alert](https://www.fbm.com/technology/publications/major-decision-affects-law-of-scraping-and-online-data-collection-meta-platforms-v-bright-data/); [MediaPost](https://www.mediapost.com/publications/article/392920/judge-sides-against-meta-in-battle-over-scraping-p.html).
  - Meta later dropped the suit and its appeal — [MediaPost](https://www.mediapost.com/publications/article/393996/meta-abandons-lawsuit-against-bright-data-over-scr.html).
- **Meta's stance on redistribution:**
  - Meta told the Lejo1 maintainer that the dumps were used "for alleged malicious behaviour" and that the data may only go to people verified for the Ad Library API — [Lejo1 README](https://github.com/Lejo1/facebook_ad_library);
  - a vendor says using archive data for ad targeting or resale breaches Meta's terms — [singhamandeep.com](https://singhamandeep.com/?p=1356) [snippet].
- **Meta's API page**, seen in search snippets only (facebook.com returns 403 to automated fetches), via the helper — [Meta Ad Library API](https://www.facebook.com/ads/library/api) [snippet]:
  - the API covers political and issue ads worldwide for 7 years, plus all ads delivered in the EU or UK over the past year;
  - access commits you to Meta's Platform Policy;
  - ad images and text may be saved "only for analysis";
  - bulk download is not supported;
  - no clause on commercial use, redistribution or competing products was retrieved.
- **TikTok:** the Research Tools Terms of Service, effective 22 Jan 2026 — [TikTok Research Tools ToS](https://www.tiktok.com/legal/page/global/terms-of-service-research-api/en) (details in section 3):
  - forbid use "for any commercial or unauthorized purpose";
  - require refreshing data every 30 days and deleting what is no longer available;
  - bar sharing any data "derived or aggregated from" it.
- **Google:**
  - both datasets are governed by the Google Terms of Service and the Ads Transparency Center Additional Terms — [README](https://storage.googleapis.com/ads-transparency-center/api-data/README.txt);
  - Google's list of service-specific additional terms includes an Ads Transparency Center row — [Google service-specific terms](https://policies.google.cn/terms/service-specific?hl=en) [snippet];
  - the Transparency Center page's own code handles a 503 "your computer or network may be sending automated queries" response (helper, page source);
  - third-party scraping services "sit outside Google's terms" — [AdMakeAI](https://admakeai.com/blog/google-ads-transparency-center) [vendor].
- **X:** its terms bar independent access including scraping; the Commission counted this against X in its 5 Dec 2025 decision — [Commission](https://digital-strategy.ec.europa.eu/en/news/commission-fines-x-eu120-million-under-digital-services-act).
- **Microsoft:** anonymous Ad Library API use falls under the Microsoft Developer Terms of Use, with "stricter limits" — [Microsoft Learn](https://learn.microsoft.com/en-us/advertising/guides/ad-library-api).
- **LinkedIn** returned "You are unable to access linkedin.com" (403) to plain curl; its API is gated (section 4).
- **France, CNIL:**
  - In June 2025 the CNIL published a practice sheet on collecting personal data by web scraping under legitimate interest. It came with its AI recommendations and sets safeguards to limit intrusion — [CNIL focus sheet](https://www.cnil.fr/fr/focus-interet-legitime-collecte-par-moissonnage); [Hogan Lovells summary](https://www.hoganlovells.com/fr/publications/development-of-an-ai-system-cnil-issues-guidelines-regarding-collection-of-data-via-web-scraping).
  - Its detailed measures were not read: the page answered 503.
- **EU database law:** CJEU Case C-30/14, *Ryanair v PR Aviation*, judgment of 15 Jan 2015, concerns contractual limits on reusing a database's data — [Kluwer Copyright Blog](https://copyrightblog.kluweriplaw.com/category/jurisdiction-2/page/90/).
- **Personal data in ad data:** the DSA repository must not contain personal data of recipients — [Art. 39(1)](https://www.eu-digital-services-act.com/Digital_Services_Act_Article_39.html). It does contain advertiser and payer names, which can be natural persons, for example LinkedIn's `advertiser.promotor` for ads run under an individual's name — [SearchAPI LinkedIn docs](https://www.searchapi.io/docs/linkedin-ad-library-api).

### Inferences
- **For a private, internal weekly ranking, the legal risk is low** if you use the official APIs and the BigQuery dataset, store aggregates per advertiser, and drop natural-person advertisers or pseudonymise them.
- **The risk rises with:**
  - republishing raw library data, which runs against Meta's stated position;
  - hammering undocumented endpoints, which breaches terms and gets IPs blocked;
  - selling the dataset.
- **Art. 40(12) research access is closed to a commercial project.** Do not frame the tool as research to get access.
- **TikTok is the clearest contractual limit.** If the Research Tools terms govern the CCAPI, a commercial tracker cannot use it, and even aggregates derived from it cannot be shared. There are two ways forward:
  - get TikTok's answer in writing;
  - read TikTok through SearchAPI's scraped `tiktok_ads_library` instead, accepting the terms-of-service risk of scraping.

### Gaps
- Not read in full, and should be before building:
  - Meta's Ad Library API terms (403);
  - the TikTok Developer Terms of Service (fetch failed);
  - LinkedIn's API terms;
  - Google's Ads Transparency Center Additional Terms (a JavaScript page) and the BigQuery dataset's licence;
  - the CNIL sheet's measures (503).
- Recalled by the helper but not verified in this session:
  - LinkedIn's User Agreement §8.2 bans scraping;
  - hiQ v. LinkedIn: the 9th Circuit ruled on the CFAA in 2022; a Nov 2022 ruling found hiQ had breached the User Agreement; the case settled in Dec 2022;
  - the database right forbids repeated systematic extraction (BHB v William Hill, C-203/02);
  - GDPR Art. 14 requires a notice when advertisers are natural persons.
- The Ryanair holding is summarised from secondary sources only. Commonly reported, but not verified here: website terms can restrict extraction from databases that the Database Directive does not protect. Check it on CURIA.

## 10. Recommended weekly pipeline for "new top spenders per category" (France/EU first, US second), and the pitfalls of this signal

### Takeaway
**France/EU** can be done for €0–40 a month with official sources:
- **Google:** the BigQuery dataset, with 56 topics, fresh creative counts and 90-day-lagged impressions;
- **Meta:** the official API, with weekly snapshots of EU reach per ad;
- **TikTok:** CCAPI daily ad counts per advertiser and unique users seen, if TikTok's terms allow commercial use (section 9), otherwise SearchAPI's scraped library;
- **Snapchat:** exact impressions per country;
- **Microsoft:** impression bands;
- **LinkedIn:** for B2B ideas.

**The US** has no platform exposure data for commercial ads. It needs:
- SE Ranking monthly paid-search history (who started bidding, estimated traffic cost);
- SearchAPI weekly snapshots of Meta and Google creatives (active ads, new ads per week, variants, rank under the impressions sort);
- optionally SpyFu or Semrush (under €100) for Google spend history.

The output is a ranked list per category of advertisers whose exposure or creative velocity jumped, and of new entrants that are already large. The list is a lead generator for "people pay to acquire customers here", not a spend measurement.

### Cited Findings
- Feasibility per platform, as established in sections 1–6 with their sources:

| Platform | Region | Who is advertising | Exposure number | Dates | Category | Cost | Access |
|---|---|---|---|---|---|---|---|
| Google (BigQuery `creative_stats`) | EEA + TR | Yes, all advertisers | Impression bounds per country and surface, **90-day lag** | first/last shown, 1-day lag | `topic` (56) | Free within 1 TiB/month | Google account |
| Google (SearchAPI or SerpApi) | US + all | By domain or advertiser | None | first/last shown, days shown | ad-details `topic` | ~$3–4 per 1k calls | Key |
| Meta (official API) | EU/UK commercial | Keyword, page, or `*` | `eu_total_reach`, reach by age × gender × country | start/stop | Page categories via the web | Free | ID check + app |
| Meta (SearchAPI web) | US + all | Keyword or page | Rank only (impressions sort) | start/end, active time | `page_categories` | ~$3–4 per 1k | Key |
| TikTok (CCAPI) | 32 European countries | Keyword, advertiser | `unique_users_seen` (+ breakdowns); daily ad counts per advertiser | first/last shown | Objective only | Free | Application; Research Tools terms forbid commercial use (applicability to the CCAPI unverified) |
| Snapchat (Ads Gallery API) | EU | Substring of payer name | **Exact** impressions per country | start date | None | Free | None |
| Microsoft (Ad Library API) | EEA | List by country and date | Impression band + % per country | start/end | None | Free | None (anonymous) or token |
| LinkedIn | EU-targeted | Keyword, advertiser | Estimated impressions + % per country | run dates | None | Gated API or SearchAPI | Gated |
| Pinterest | EU | Advertiser, category | EU reach in 10K bands | display period | Category filter | Free (web) | None |
| Apple App Store | EU | All ads per country | None | first/last impression | None (derive from the app) | Free | None |
| SE Ranking (Google Search) | FR, US + others | By keyword or domain | Est. paid traffic and traffic cost, monthly | Monthly | Via keywords | 100 credits/call | Key |

- CPM inputs for converting exposure into euros: Meta France about $7–9 and US about $16–23 in 2026 (section 1). Microsoft notes its library is meant "for regulatory visibility rather than performance analysis" — [Microsoft Learn](https://learn.microsoft.com/en-us/advertising/guides/ad-library-api).

### Inferences

#### Weekly pipeline: France and the EU (run on Mondays, store everything in DuckDB or Parquet)

1. **Google (BigQuery, free).**
   - Run the section 2 query for `region_code='FR'` (and DE, ES and IT if wanted).
   - Store per advertiser and topic: `new_28d`, `new_prev_28d`, `active_7d`, `first_seen_fr` and the lagged impression midpoints.
   - Also insert the per-creative FR bounds snapshot, for lagged weekly impression deltas.
   - Resolve the top 200 advertisers to landing domains, through SearchAPI `google_ads_transparency_center_ad_details` (about 200 calls a week) or the creative page.
2. **Meta (official API, free).**
   - For each category, run 20–50 French seed keywords: `ads_archive?ad_reached_countries=['FR']&ad_type=ALL&ad_active_status=ALL&ad_delivery_date_min=<today-7>`.
   - Fields: `id`, `page_id`, `page_name`, `ad_delivery_start_time`, `ad_delivery_stop_time`, `eu_total_reach`, `age_country_gender_reach_breakdown`, `beneficiary_payers`, `publisher_platforms`, `ad_creative_link_captions`, `ad_creative_link_titles`.
   - Optionally add a full-country crawl with `search_terms='*'`, if throughput allows.
   - Each week, re-fetch reach for ads already known (by `search_page_ids`, 10 per call).
   - Per page and week, compute ΔFR reach (the sum of FR rows in the breakdown, differenced against last week), new ads started in the last 7 days, active ads, and the share of active ads older than 30 days.
   - Estimated spend = ΔFR reach × f × CPM_FR / 1000, with f between 1.5 and 2.5 and CPM_FR between about $7 and $9; always report it as a range.
3. **TikTok (CCAPI, free after approval).**
   - Check eligibility and terms first: TikTok's Research Tools terms forbid commercial use and sharing derived data (section 9). If they apply, take the same signals (unique-users bands, first and last shown) from SearchAPI's `tiktok_ads_library` instead.
   - Discover advertisers with the ad query: category keywords, `country_code_list=['FR']`, last 7 days of publication, `ad_reach=['100K+','10K-100K']`.
   - For the business IDs found, pull `ad/report` `count_time_series_by_country` over 90 days, which gives ads per day in FR.
   - From ad details, take FR `unique_users_seen` for their new ads.
4. **Snapchat (free).**
   - Sweep `ads/search` with `countries=['fr']`, last 7 days, and a rotating set of 2–3-letter substrings.
   - De-duplicate by ad ID, store `impressions_map.fr`, and compute the weekly Δ per `paying_advertiser_name`.
5. **Microsoft (free).**
   - Call `Ads?countryCodes=66&startDate=d&endDate=d` for each day, to stay under the apparent 1,000 cap.
   - Pull `Ads({id})` details for new ads, and store `TotalImpressionsRange` and the FR share.
6. **LinkedIn, B2B categories only.**
   - Run SearchAPI `linkedin_ad_library` with `country=FR` and `time_period=last_30_days` on B2B keywords, plus ad details for the impression bands.
7. **Category mapping.**
   - Google: `topic`.
   - Meta: `page_categories` (from SearchAPI on demand) or a cheap LLM classification of the landing domain into the same 56-topic taxonomy.
   - TikTok: `advertising_objective` plus a domain classification.
   - Use one taxonomy across platforms.
8. **Scoring, per category and country.**
   - Weekly exposure growth = exposure over the last 4 weeks ÷ (the previous 4 weeks + k).
   - Creative velocity ratio, scored against the advertiser's own history.
   - A new-entrant flag (first seen within 60 days, or a TikTok account created recently via the `business_id >> 32` trick [local note]).
   - Cross-platform agreement: the number of platforms where the advertiser is rising.
   - Flag the "new top spenders": in the top decile of exposure in their category **and** either a new entrant or growth above 2× quarter over quarter.
   - Exclude the stable top 1% and known marketplaces and agencies.
   - Output: 20 advertisers per category, each with its evidence (links to ads, reach, dates).

#### Weekly pipeline: US (about €40–100 a month)

1. **Google Search (SE Ranking, monthly).**
   - Run `domain/ads?keyword=…&source=us&from=<m-3>&to=<m>` for about 30 seed keywords per category.
   - Then run `overview/history?type=adv` on the domains that appear.
   - Rank by month-over-month growth of `price_sum` and `keywords_count`, plus `keywords_new_count`.
2. **Google, all formats (SearchAPI, weekly).**
   - For candidate domains, run `google_ads_transparency_center` with `region=US` and `time_period=last_7_days`.
   - Store creative IDs and `first_shown`, and compute new creatives per week. Remember the 200-per-region cap reported in v1.
3. **Meta (SearchAPI, weekly).**
   - Run `meta_ad_library` with `country=US`, `active_status=active` and `sort_by=impressions_high_to_low` on category keywords.
   - For each page, compute active ads, ads started in the last 7 days, the sum of `collation_count`, and the median rank position.
   - Snapshot every week; growth comes from comparing snapshots.
4. **TikTok.**
   - A Creative Center check of Top Products by category in the US (popularity change), as a trend cross-check only.
5. **Optional, under €100.** SpyFu or Semrush Advertising Base, for 12+ months of Google Search spend history on the shortlist, to tell "new" from "returning".

#### Pitfalls of the signal
- **No platform publishes commercial spend.** Every euro figure is a model built on assumed frequency and CPM (sections 1 and 8). Rank on exposure deltas and report euros as ranges.
- **Exposure numbers are EU-only:** Meta reach, TikTok users, Snapchat impressions, Google impression bounds, Microsoft and LinkedIn bands. US rankings rest on proxies: counts, dates, rank order, and SE Ranking's modelled search traffic.
- **Google impressions lag 90 days.** Creative counts are fresh. `first_shown` is clipped at 2023-03-01. The Cloud Storage folder still holds stale 2025 shards.
- **Identity:**
  - Google's "advertiser" is often an agency or reseller;
  - the domain filter mixes affiliates;
  - Meta keyword search is noisy and full of name collisions;
  - Snapchat's name match is a substring.
  - Resolve every advertiser to a landing domain before ranking [local note; section 2 live check].
- **Longevity and count confounders:**
  - retargeting and brand ads run long without scaling;
  - restarts reset dates;
  - DCO and catalogue (DPA) ads multiply "ads";
  - about half of launched ads get no meaningful budget, and about 5% take most of it (Motion).
- **Seasonality:** Q4 and Black Friday CPMs and creative bursts (US CPM above $30 in Black Friday week — [Adligator](https://adligator.com/blog/meta-ads-cpm-by-country-benchmarks) [snippet]). Compare with the category baseline for the same weeks, or year over year once a year of data exists.
- **Survivorship and retention:** ads leave the libraries one year after their last impression, and Meta's API defaults to active ads only. History you did not snapshot is lost.
- **Repository gaps:**
  - ads seen in feeds are sometimes missing from the repositories (Mozilla/CheckFirst 2024);
  - in April 2026, previously findable ads could disappear from Meta's repository, and most Snapchat feed ads were absent from its archive ([ÖIAT](https://research.oiat.at/fileadmin/Research/Dokumente/PolicyBrief_AdWatch_AdLibraries_EN.pdf));
  - TikTok was found in breach in 2025, and its commitments were not implemented as of April 2026.
  - A weekly snapshot therefore undercounts, unevenly by platform; compare advertisers within a platform, not across platforms.
- **Terms:** TikTok's Research Tools terms forbid commercial use. Meta allows saving creatives "only for analysis", and Meta has told an archive maintainer to restrict its dumps. Keep the dataset internal and aggregate.
- **Quotas:**
  - Meta's per-app limits (15 apps at most, per one maintainer);
  - SearchAPI credit exhaustion, which looks like a 429;
  - TikTok web search throttling;
  - SE Ranking 429s;
  - CCAPI returns 10 results per call.
- **Rising spend is not profitability.** It can be funded growth, a launch burst or a failing test. Use "still rising after 6–8 weeks" and old-ad survival as the profit-leaning filters, and treat the output as hypotheses to verify, for example by checking the landing page, the price and app reviews.

### Gaps
- **Not run end to end.**
  - The BigQuery SQL was not executed: no GCP credentials were used.
  - The Meta, TikTok and LinkedIn API calls were not made: no keys were used today.
  - Byte counts, rate limits and costs are estimates.
- **Not validated.**
  - No ground truth tells whether reach deltas rank advertisers the same way their real spend would.
  - A first validation: compare the pipeline's ranking with the spend of a few accounts whose real budgets are known.
