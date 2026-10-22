# Where business buyers write down their pains in public, and how to mine those places for paid problems (state as of 22 October 2026)

*Method note: on top of web research, this run made live calls on 2026-10-22 between 10:04 and 11:10 UTC. It used plain HTTP clients (curl and Python urllib, a browser-like User-Agent, no login) from one residential IP in France; GitHub search alone used an authenticated `gh` token. A citation marked "probe" links the exact endpoint called. Results can differ by IP, user agent and time. Vendor pages are labeled as vendor content.*

## 1. Reddit: API access in 2025-2026, the `.json` endpoints, the archives, the monitoring tools, and the subreddits dense with paying buyers

### Takeaway
Since November 2025, any use of Reddit's API needs explicit approval under the Responsible Builder Policy, and commercial use needs separate written approval. Unauthenticated `.json` requests are blocked: the probes got a 403 or a redirect to login. RSS feeds, including search RSS, still answer. Arctic Shift is the live successor archive: an API minutes behind live Reddit, plus monthly dumps through 2026-09. Reddit's policy grants no right to mine it commercially. GummySearch closed because it could not get a commercial license. F5Bot and Syften still run.

### Cited Findings

#### Official policy (primary sources)
- The Responsible Builder Policy (RBP) says it applies to "everyone—whether you're a developer, moderator, researcher, or an app". Its first rule: "Approval is required: You must request access and get explicit approval before accessing any Reddit data through our API". It also prohibits misrepresenting why you access the data, including "registering multiple accounts or submitting multiple requests for the same use case". — [Reddit Help: Responsible Builder Policy](https://support.reddithelp.com/hc/articles/42728983564564). The article was created 2025-10-28 and last edited 2026-10-05. The HTML page returns 403 to non-browser clients, so it was read through the help center's [public JSON](https://support.reddithelp.com/api/v2/help_center/en-us/articles/42728983564564.json).
- RBP: developers of non-commercial apps "should use the Developer Platform ('Devvit')". "If you'd like to use Reddit data for commercial purposes, you'll need to get explicit written approval." — [Responsible Builder Policy](https://support.reddithelp.com/hc/articles/42728983564564)
- RBP: "You must not sell, license, share, or otherwise commercialize Reddit data without express written approval. This extends to commercial and non-commercial mining, scraping, or using data for purposes like ads targeting or to train machine learning or AI models." — [Responsible Builder Policy](https://support.reddithelp.com/hc/articles/42728983564564)
- RBP: the Reddit for Researchers (RFR) program is "solely for non-commercial purposes", and "Any research that uses Reddit data collected outside of the RFR Program is in violation of this policy." The policy bans inferring sensitive traits and re-identifying users. Enforcement includes revoking tokens and "Suspending associated accounts, bots, domains, or subreddits". — [Responsible Builder Policy](https://support.reddithelp.com/hc/articles/42728983564564)
- Announcement: the r/redditdev post of 11 Nov 2025, "Introducing the Responsible Builder Policy + new approval process", ended self-service API access. Existing access is kept if it stays compliant, Devvit is recommended, and researchers open a ticket. A reproduced rejection message says requests with full detail are favored. — [third-party mirror of the r/redditdev post](https://r.datuan.dev/r/redditdev/comments/1oug31u/introducing_the_responsible_builder_policy_new/nyz3hqg/?context=3) (seen only through search snippets)
- Data API Wiki: "Clients must authenticate with a registered OAuth token." It requires a unique User-Agent of the form `<platform>:<app ID>:<version string> (by /u/<username>)`. "Traffic not using OAuth or login credentials will be blocked." The free-access limit is "100 queries per minute (QPM) per OAuth client id", averaged over a 10-minute window. Content deleted on Reddit must be deleted, and Reddit "strongly recommend[s] routinely deleting any stored user data and content within 48 hours". — [Reddit Data API Wiki](https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki), edited 2026-05-11, read through its [JSON](https://support.reddithelp.com/api/v2/help_center/en-us/articles/16160319875092.json)
- Data API Terms ("Effective June 19, 2023. Last Revised July 20, 2026"): "If you are interested in using the Data APIs for commercial purposes, research in excess of rate limits, or for any use that is not expressly permitted ... you will need to enter into a separate agreement with Reddit." Users may not "derive revenues from the use or provision of the Data APIs" without express written approval, and may not train ML/AI models on User Content without the rightsholders' permission. "Reddit reserves the right to charge fees for future use". — [Reddit Data API Terms](https://redditinc.com/policies/data-api-terms)
- Developer Terms ("Last Revised March 24, 2026"): Reddit may require App Review "prior to distributing it ..., after hitting API rate limits, or at any time". Section 4.1 covers commercial-use restrictions: commercial use needs a separate agreement. Crawling to train models without permission is prohibited. Encryption at rest and deletion controls are required. — [Reddit Developer Terms](https://redditinc.com/policies/developer-terms)
- No official public price for commercial access was found. One vendor claims "a $12,000-a-year Standard tier plus per-call fees" — [redditapis.com](https://www.redditapis.com/reddit-responsible-builder-policy) (it sells an approval-free alternative). Another says commercial fee rates are not publicly documented — [vorplabs.com](https://vorplabs.com/agent-tools/reddit-data-api). The two conflict and neither is verified.
- Enforcement: on 22 Oct 2025, Reddit sued Perplexity, SerpApi, Oxylabs and AWMProxy in Manhattan federal court over "industrial-scale" scraping of Reddit content through Google results. It had sued Anthropic in June 2025, and it has data deals with Google and OpenAI. — [BNN Bloomberg / AP](https://www.bnnbloomberg.ca/business/2025/10/22/reddit-sues-ai-company-perplexity-and-others-for-industrial-scale-scraping-of-user-comments); [Search Engine Land](https://searchengineland.com/reddit-sues-perplexity-serpapi-scraping-google-463681). No outcome was found.

#### Do the public `.json` endpoints still work? (probes, 2026-10-22)
- `www.reddit.com/r/smallbusiness/search.json?...` returned HTTP 403 (an HTML block page) — [probe](https://www.reddit.com/r/smallbusiness/search.json?q=%22is%20there%20a%20tool%22&restrict_sr=1&sort=new&limit=3). `www.reddit.com/r/smallbusiness/new.json` also returned 403 — [probe](https://www.reddit.com/r/smallbusiness/new.json?limit=2).
- `old.reddit.com/r/smallbusiness/new.json` returned a 302 redirect to `/login/?reason=lor2` — [probe](https://old.reddit.com/r/smallbusiness/new.json?limit=3).
- RSS is still served. `/r/smallbusiness/new/.rss` returned 200 with an Atom feed — [probe](https://www.reddit.com/r/smallbusiness/new/.rss). Search RSS (`/r/smallbusiness/search.rss?q="is there a tool"&restrict_sr=on&sort=new`) returned 200 with matching titles, such as "How do businesses in Canada keep track of taxes, filings and deadlines for their business? Is there a tool currently available in the market...?" — [probe](https://www.reddit.com/r/smallbusiness/search.rss?q=%22is+there+a+tool%22&restrict_sr=on&sort=new)

#### Archives: Arctic Shift, Pushshift, PullPush
- Arctic Shift, by Arthur Heitmann, offers bulk dumps, a "limited" API and web tools (search, a download tool) "for academics, community moderators, and the public". It has a removal-request form. The repo page states no license and no commercial-use terms. — [GitHub: arctic_shift](https://github.com/ArthurHeitmann/arctic_shift)
- The API:
  - Base URL `https://arctic-shift.photon-reddit.com`, with `/api/posts/search` and `/api/comments/search`.
  - Filters: author, subreddit, after/before, title/selftext/query (posts only) and body (comments only).
  - Full-text search on `title` and `body` works only alongside author/subreddit (or link_id/parent_id), and is "not supported with very active users or subreddits".
  - `limit` runs from 1 to 100, or `auto` for 100–1000 results.
  - "Rate limits are calculated dynamically based on server load and request complexity."
  - Freshness: "After roughly 36 hours, all data is updated". Before that, score and comment counts read 0 or 1.
  - Caveats: "No uptime or performance guarantees". "This is a free service, so be considerate", with a pointer to the monthly dumps for bulk work.
  - The README marks its own full-text section "out of date".
  — [Arctic Shift API README](https://github.com/ArthurHeitmann/arctic_shift/blob/master/api/README.md)
- Dumps: as of 2026-10-22, the monthly releases are listed through 2026-09. Torrents are on Academic Torrents, in zst or zst_blocks format. — [download_links.md](https://github.com/ArthurHeitmann/arctic_shift/blob/master/download_links.md)
- Probes:
  - Posts by subreddit and date returned 200. The newest post was created 2026-10-22 09:56:15 UTC, about 8 minutes before the probe. Its titles included "What AI tools are actually worth paying for in a small business?" — [probe](https://arctic-shift.photon-reddit.com/api/posts/search?subreddit=smallbusiness&after=2026-10-15&limit=3&fields=title,created_utc)
  - Posts with `query=spreadsheet` returned 422 "Timeout. Maybe slow down a bit", on both r/smallbusiness and the small r/bookkeeping — [probe](https://arctic-shift.photon-reddit.com/api/posts/search?subreddit=bookkeeping&query=spreadsheet&limit=3).
  - Comment `body=` search worked on r/bookkeeping, r/msp, r/restaurantowners and r/sweatystartup. Each hit the 100-result cap for the last 365 days. — [probe](https://arctic-shift.photon-reddit.com/api/comments/search?subreddit=bookkeeping&body=%22would%20pay%22&limit=3&fields=body,created_utc)
  - Comment search is not exact-phrase. `"we pay"` returned comments containing "I pay" or "if I charge". `"is there a tool"` returned comments that lack the phrase. — [probe](https://arctic-shift.photon-reddit.com/api/comments/search?subreddit=msp&body=%22is%20there%20a%20tool%22&limit=100)
  - The aggregate endpoint returned 400 on the parameters tried — [probe](https://arctic-shift.photon-reddit.com/api/comments/search/aggregate?aggregate=created_utc&frequency=year&subreddit=bookkeeping&body=spreadsheet).
- Secondary claims (unverified):
  - A Parquet dataset of about 2.5 billion items through Feb 2026, roughly 261 GB, updated monthly.
  - A blogger's check on 22 Aug 2026 put the API about 30 seconds behind live Reddit, with heavier requests often failing.
  — [jwatte.com](https://jwatte.com/blog/reddit-data-arctic-shift-for-business/), [xpoz.ai](https://www.xpoz.ai/blog/tutorials/how-to-get-historical-reddit-data-after-pushshift/) (seen through search summaries)
- Pushshift: `api.pushshift.io` returned 403 `{"detail":"Not authenticated"}` — [probe](https://api.pushshift.io/reddit/search/submission?subreddit=smallbusiness&size=1).
- PullPush: `api.pullpush.io` returned 429 at probe time, and `pullpush.io` returned 403 — [probe](https://api.pullpush.io/reddit/search/submission/?subreddit=smallbusiness&size=2).

#### Monitoring tools
- **GummySearch is closed.** The closing page says it is "shutting down to comply with Reddit's API policies, which forbid commercial applications". It closed on November 30th, 2025. Subscribers keep access until the end of their current payment cycle ("max 1 year"), and lifetime-deal holders "until 11/30/2026". Free users can only download their data. — [GummySearch: closing time](https://gummysearch.com/closing-time)
- The founder's post of Nov 6, 2025: "we were not able to reach an agreement that aligns with Reddit's Data API Usage policies". "Over 135,000 founders, marketers, and investors" had relied on the product. The service ends December 1, 2026, and user data is then deleted. — [GummySearch: final chapter](https://gummysearch.com/final-chapter)
- **F5Bot** monitors "Reddit, Hacker News, and Lobsters" (Reddit posts and comments "in every subreddit") and checks "every few minutes".
  - Free plan: email alerts, more limited filtering.
  - Silver, $9.99/month: 20 keywords.
  - Gold, $49.99/month: 200 keywords, RSS and JSON feeds, AI filtering, Slack and Discord delivery.
  — [F5Bot](https://f5bot.com/)
- **Syften** covers Reddit, Hacker News, Indie Hackers, Bluesky, Mastodon, X/Twitter ("a delay of at most 15 minutes"), GitHub, Product Hunt, Lobste.rs, Dev.to, Stack Exchange, forums, newsletters, podcasts, YouTube and "assorted Slack groups". It does not cover LinkedIn ("No, unfortunately not").
  - Entry, $29.95/month: 3 community filters, 100 community results/day, 7-day archive.
  - Standard, $49.95/month: 20 filters, 200 results/day, 30-day archive, Slack delivery, AI noise filter, API.
  - PRO, $119.95/month: 100 filters, 500 results/day, webhooks, MCP, and archive search up to 1,000,000 items/month.
  - Add-ons: X at "+$40.00/month" and YouTube at "+$20.00/month".
  - A 14-day trial runs on PRO. The Reddit "target delay [is] under 1 minute".
  — [Syften](https://syften.com/)
  - A competitor says Syften bills in euros. — [RedShip](https://redship.io/reddit-tool/syften) (vendor)
- Other Reddit monitors and GummySearch replacements are promoted on vendor pages: notifier.so, RedShip, Redditapis, xpoz, socialcrawl. None was evaluated. — [notifier.so](https://notifier.so/blog/?p=5440), [xpoz.ai](https://www.xpoz.ai/blog/comparisons/best-gummysearch-alternatives-2026/), [socialcrawl.dev](https://www.socialcrawl.dev/vs/gummysearch), [rdk.taprun.dev](https://rdk.taprun.dev/alternatives/gummysearch)
- Apify Reddit scrapers, all priced pay-per-event: [trudax/reddit-scraper-lite](https://apify.com/trudax/reddit-scraper-lite) (49,162 users, 8,348 in the last 30 days), [fatihtahta/reddit-scraper-search-fast](https://apify.com/fatihtahta/reddit-scraper-search-fast) (64,667 users), [harshmaur/reddit-scraper](https://apify.com/harshmaur/reddit-scraper) (17,441 users). Several "Reddit lead finder" actors score posts for buying intent: [logiover/reddit-lead-finder](https://apify.com/logiover/reddit-lead-finder), [fayoussef/reddit-lead-finder](https://apify.com/fayoussef/reddit-lead-finder). — figures from the [Apify Store API](https://api.apify.com/v2/store?search=reddit%20scraper) (probe)

#### Subreddit sizes (Arctic Shift subreddit metadata; probe 2026-10-22; the capture date of the counts is not shown)
| Subreddit | Subscribers | Posts archived | Comments archived |
|---|---|---|---|
| r/Entrepreneur | 4,547,610 | 766,651 | 5,319,893 |
| r/RealEstate | 2,240,939 | 374,514 | 5,321,575 |
| r/smallbusiness | 1,939,492 | 387,349 | 3,747,641 |
| r/marketing | 1,763,790 | 280,094 | 1,204,448 |
| r/Accounting | 1,105,368 | 493,741 | 5,454,924 |
| r/sysadmin | 977,787 | 539,152 | 11,156,457 |
| r/excel | 763,575 | 426,932 | 2,575,936 |
| r/freelance | 580,727 | 107,831 | 303,459 |
| r/ecommerce | 513,748 | 124,095 | 638,068 |
| r/electricians | 480,181 | 306,722 | 4,676,281 |
| r/Construction | 442,223 | 195,946 | 3,132,517 |
| r/Plumbing | 413,383 | 504,234 | 4,351,354 |
| r/sales | 387,191 | 227,505 | 2,314,780 |
| r/Notion | 385,568 | 97,908 | 532,781 |
| r/SEO | 371,629 | 448,912 | 1,349,556 |
| r/consulting | 304,502 | 108,631 | 1,096,724 |
| r/Truckers | 304,478 | 237,332 | 4,458,574 |
| r/shopify | 273,977 | 132,367 | 705,703 |
| r/HVAC | 204,578 | 226,474 | 2,815,401 |
| r/PPC | 200,970 | 108,206 | 710,499 |
| r/msp | 196,754 | 78,187 | 1,336,686 |
| r/projectmanagement | 176,686 | 52,944 | 334,900 |
| r/EtsySellers | 176,680 | 124,442 | 994,185 |
| r/sweatystartup | 159,967 | 16,595 | 185,488 |
| r/Insurance | 155,185 | 209,833 | 1,860,448 |
| r/realtors | 140,323 | 72,721 | 1,061,718 |
| r/Dentistry | 138,856 | 308,047 | 1,420,959 |
| r/FulfillmentByAmazon | 113,357 | 67,147 | 477,460 |
| r/Lawyertalk | 112,129 | 67,712 | 1,375,225 |
| r/salesforce | 86,548 | 65,094 | 497,490 |
| r/AmazonSeller | 75,206 | 31,821 | 131,579 |
| r/LawFirm | 72,624 | 30,065 | 392,116 |
| r/nocode | 55,328 | 29,925 | 142,279 |
| r/Bookkeeping | 49,503 | 26,572 | 177,654 |
| r/agency | 43,962 | 24,129 | 148,437 |
| r/restaurantowners | 36,039 | 22,778 | 258,777 |
| r/QuickBooks | 28,097 | 34,155 | 131,638 |
| r/hubspot | 11,266 | 9,762 | 57,165 |
— source: [Arctic Shift subreddit search API](https://arctic-shift.photon-reddit.com/api/subreddits/search?subreddit=smallbusiness), one probe per name. The r/propertymanagement lookup returned 422.

### Inferences
- **Compliance ladder for Reddit, from safest to riskiest:**
  1. Read in a browser as an ordinary user, and take Sales-Safari-style notes.
  2. Poll RSS (including search RSS) for personal alerts. It works today, but the RBP and the Data API Terms do not say whether RSS counts as "the API" (see Gaps).
  3. Pay a monitoring vendor (F5Bot, Syften). The compliance burden then sits with the vendor, but whether either holds a Reddit commercial license is not stated, and GummySearch shows such tools can disappear.
  4. Apply for approved OAuth access, stating the purpose honestly. A commercial idea-mining tool needs written commercial approval.
  5. Use Arctic Shift, PullPush or Apify scrapers for commercial mining. The RBP explicitly covers "commercial and non-commercial mining, scraping" without approval, and Reddit is suing scrapers.

  For a one-founder idea factory, steps 1–3 are the realistic zone.
- **Arctic Shift is the best free source for history and backfill.** Its posts API is near real-time, and the dumps run through 2026-09. Three things limit it. Full-text search fails on big subreddits. Comment search is token-based, so every hit needs local regex post-filtering on the exact phrase. And its legal footing for commercial use is weak: it states nothing, and Reddit says data collected outside its programs violates policy.
- **Buyer density by community** (judged from each community's purpose and size, not measured):
  - Owners with budgets: r/msp (MSP owners buy RMM/PSA and security tools), r/sweatystartup (service-business owners), r/Bookkeeping (solo practices), r/LawFirm (firm owners), r/restaurantowners, r/realtors (agents pay for CRMs and leads), r/EtsySellers, r/FulfillmentByAmazon, r/AmazonSeller and r/shopify (merchants paying app and fee stacks), r/PPC and r/agency (agencies buying ad tools), r/Dentistry (practice owners, though students too).
  - Workaround builders and existing paid-tool users: r/excel (spreadsheet workarounds are pain evidence) and r/QuickBooks, r/salesforce, r/hubspot, r/Notion (users of a paid tool asking for missing features).
  - Mostly employees or technicians, who influence purchases more than they make them: r/sysadmin, r/Accounting, r/sales, r/HVAC, r/electricians, r/Plumbing, r/Construction.
  - Founder- and aspirant-heavy, so supply-side noise: r/Entrepreneur and, to a lesser degree, r/smallbusiness.
- Reddit queries that surface money:
  - Combine a money or behavior marker with a domain noun inside a buyer-dense subreddit. For example, in r/Bookkeeping: `"we pay" OR "per month" OR "subscription"` plus a tool category; in r/msp: `"is there a tool" OR "alternative to"` plus a vendor name.
  - Track named-vendor switching posts ("switching from X", "X alternative", "X raised prices").

### Gaps
- No official commercial price or approval criteria for the Reddit Data API were found. The vendors' $12k/year claim is unverified.
- The text read does not say whether RSS polling counts as "the API" under the RBP. Nor does it define "commercial purposes" for internal market research by a for-profit person.
- Whether F5Bot or Syften hold Reddit commercial licenses is not stated on their sites.
- Pushshift's current access rule was not re-verified (only the "Not authenticated" response was seen). PullPush's status is unclear because the probe was rate-limited.
- Subscriber counts come from Arctic Shift metadata with no capture date. Reddit's own `about.json` is blocked without OAuth.
- Buyer density per subreddit was not measured, for example as the share of posts mentioning spend.

## 2. Hacker News: the Algolia HN Search API and the recurring threads worth mining

### Takeaway
HN is the most open source in this catalog. The Algolia API is free and keyless, allows 10,000 requests per hour per IP, and supports date search, `ask_hn` and `comment` tags, and numeric filters. The official Firebase API has no rate limit. The audience is developers and founders, so pain threads with money attached are rarer than the volume suggests and need tight filters.

### Cited Findings
- Rate limit, from the API page: "We are limiting the number of API requests from a single IP to 10,000 per hour." — [HN Search API](https://hn.algolia.com/api) (the text sits in the page's JS bundle, fetched 2026-10-22)
- Official API: "There is currently no rate limit." It is served from `https://hacker-news.firebaseio.com/v0/` in near real time. — [HackerNews/API README](https://github.com/HackerNews/API)
- Verified features:
  - `/api/v1/search_by_date` with `tags=comment` returns newest comments first — [probe](https://hn.algolia.com/api/v1/search_by_date?query=%22I%20would%20pay%22&tags=comment&hitsPerPage=2).
  - `/api/v1/search` with `tags=ask_hn` and `numericFilters=points>300` or `created_at_i>…` works — [probe](https://hn.algolia.com/api/v1/search?query=%22what%20are%20you%20working%20on%22&tags=ask_hn&numericFilters=created_at_i%3E1775000000&hitsPerPage=6).
- Recurring or classic threads found in the probes (date, points, comments):
  - "Ask HN: What are you working on?" runs monthly. September 2026: 381 points, 1,235 comments — [item 49686380](https://news.ycombinator.com/item?id=49686380). August 2026: 325 / 1,201 — [49233423](https://news.ycombinator.com/item?id=49233423). July 2026: 292 / 1,154 — [48884984](https://news.ycombinator.com/item?id=48884984). June 2026: 312 / 1,148 — [48528779](https://news.ycombinator.com/item?id=48528779). May 2026: 290 / 1,120 — [48085993](https://news.ycombinator.com/item?id=48085993). April 2026: 347 / 1,178 — [47741527](https://news.ycombinator.com/item?id=47741527).
  - "Ask HN: What tools do you pay for today that feel overpriced or frustrating?" (2025-11-24, 9 points, 19 comments) — [46030021](https://news.ycombinator.com/item?id=46030021).
  - "Ask HN: Which abandoned proprietary software would you resurrect?" (2018-12-08, 478 / 807) — [18635010](https://news.ycombinator.com/item?id=18635010).
  - "Ask HN: What problem in your industry is a potential startup?" (2015-06-29, 231 / 245) — [9799007](https://news.ycombinator.com/item?id=9799007).
  - "Ask HN: Dev productivity tools you would pay for" (2023-06-10, 62 / 102) — [36267563](https://news.ycombinator.com/item?id=36267563).
  - "Ask HN: New web service idea that you would pay for?" (2022-02-21, 28 / 87) — [30416562](https://news.ycombinator.com/item?id=30416562).
  - "Ask HN: What is something that doesn't exist that you would pay for?" (2016-05-27, 22 / 46) — [11789869](https://news.ycombinator.com/item?id=11789869).
  - Business-owner pain threads: "Tell HN: Automatic fraud detection is making my life hell" (2023-10-27, 402 / 388) — [38038713](https://news.ycombinator.com/item?id=38038713); "Warning – Google suspended GCP services for 'verification', lost my business" (2022-11-25, 476 / 147) — [33737577](https://news.ycombinator.com/item?id=33737577).
  - A demand-signal cautionary tale: "Ask HN: We didn't get a single person to pay for our SAAS – what could be wrong?" (2017-11-19, 185 / 317) — [15732752](https://news.ycombinator.com/item?id=15732752).
- Phrase volume in HN comments over the last 365 days (probe 2026-10-22): "alternative to" 3,931 hits; "too expensive" 2,561; "spreadsheet" 1,991; "we pay" 925; "I wish there was" 709; "switching from" 669; "price increase" 605; "we're paying" 523; "happy to pay" 421; "would pay for" 420; "I would pay" 361; "any recommendations for" 116; "I'd pay for" 111; "manually every" 42; "is there a tool" 26; "looking for a tool" 26; "hired someone to" 25; "is there an app" 9; "we use excel" 2; "hired a VA" 1. — [probe pattern](https://hn.algolia.com/api/v1/search?query=%22we%20pay%22&tags=comment&advancedSyntax=true&numericFilters=created_at_i%3E1761130000)
- Precision samples from that probe:
  - The three newest "we pay" hits were off-topic: a home cleaning service, "a tool we pay to use", a trolley-problem joke.
  - The "I would pay" hits were consumer or hypothetical: fonts, executive summaries, news articles.
  - The "is there a tool" hits were developer questions: model picking, glacier tracking, OCI images.
  — same probe

### Inferences
- **HN's role is narrow.** Mine it for developer tools, infrastructure and SaaS-operations pains, and for platform-risk pains: account bans, fraud flags, price hikes by cloud and SaaS vendors. It is weak for SMB, trades and admin pains.
- The monthly "What are you working on?" threads are supply-side. They show what is being built, which helps with a competition scan, not with buyer pains.
- The money-phrase threads ("would pay for", "tools you pay for") are few and small (under 100 comments, except old classics), but each top-level comment states a need in the first person.
- Best HN recipe:
  1. Run `search_by_date` with `tags=comment`, a money or workaround phrase, and a domain noun (for example `"we pay" invoice`, `"per seat" alternative`).
  2. Add `numericFilters=created_at_i>...` to keep only the last 12–24 months.
  3. Read whole threads where `num_comments` is above 100 and the title names a vendor or a category.
- **Raw phrase volume is a poor proxy for paid pain.** "Alternative to" and "too expensive" are frequent but mostly technical or consumer talk. The rare, specific phrases ("hired someone to", "manually every") carry far more intent per hit.

### Gaps
- The Algolia API's maximum pagination depth (total hits retrievable per query) and its terms of use for commercial reuse were not verified.
- Whether `advancedSyntax=true` is needed for exact-phrase matching was not tested in isolation.
- No study measures HN's share of business buyers as opposed to developers.

## 3. Other social and community sources: X, LinkedIn, Facebook Groups, Discord and Slack, niche professional forums, Quora, Stack Exchange, YouTube, GitHub, Product Hunt, Indie Hackers

### Takeaway
Among the open, automatable sources, YouTube comments (10,000 units/day, 1 unit per `commentThreads` call), GitHub issues sorted by 👍 and Stack Exchange are free. X is now pay-per-use: $0.005 per post read, capped at 3 million post reads a month. LinkedIn, Facebook Groups and Discord prohibit scraping, and scraping LinkedIn carries real legal precedent: Proxycurl shut down after LinkedIn sued, and France's CNIL fined KASPR €240k. Use them manually. The Product Hunt API is non-commercial by default. Indie Hackers and Quora block automated fetches.

### Cited Findings

#### X (Twitter)
- Pricing is credit-based pay-per-use: "Purchase credits upfront ... Credits are deducted as you make API requests", with "No contracts, subscriptions, or minimum spend". Reads are "Charged per resource returned". Rates: Posts: Read $0.005 per resource; User: Read $0.010; Counts: Recent $0.005 per request; Counts: All $0.010 per request; Trends $0.010 per request; owned reads $0.001 per resource. — [X API pricing](https://docs.x.com/x-api/getting-started/pricing)
- "Pay-per-usage plans are capped at 3 million Post reads per monthly billing cycle". Above that, an Enterprise plan is needed. Recent search and full-archive search both count toward the cap. — [X API pricing](https://docs.x.com/x-api/getting-started/pricing); [X post cap](https://docs.x.com/x-api/fundamentals/post-cap). Secondary sources give a 2 million cap and Enterprise at about $42,000/month; the official docs say 3 million. — [WebSearch summary of bundle.social / postproxy.dev](https://www.postproxy.dev/blog/x-api-pricing-2026/)
- Incentives: $20 in free credits on the first purchase, a match of the first auto-recharge up to $50, and free xAI API credits of 10–20% depending on spend per cycle. — [X API pricing](https://docs.x.com/x-api/getting-started/pricing)
- Pay-per-use started in early 2026; reports give 6 Feb or 21 Jan. The legacy $200 Basic and $5,000 Pro plans remain only for existing subscribers. — [MediaNama, Feb 2026](https://www.medianama.com/2026/02/223-x-developer-api-pricing-pay-per-use-model/); [postproxy.dev](https://www.postproxy.dev/blog/x-api-pricing-2026/) (secondary)
- Syften offers X monitoring as a "+$40.00/month" add-on, with "a delay of at most 15 minutes". — [Syften](https://syften.com/)

#### LinkedIn
- The User Agreement prohibits users from: "Develop, support or use software, devices, scripts, robots or any other means or processes (such as crawlers, browser plugins and add-ons or any other technology) to scrape or copy the Services, including profiles and other data from the Services". It also bans bypassing "access controls or use limits" and using "bots or other unauthorized automated methods". — [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement)
- Proxycurl (Nubela) stopped operating on 4 July 2025, about six months after LinkedIn's January 2025 complaint alleging fake-account harvesting. The founder says the case settled with a permanent injunction ordering deletion of the data. LinkedIn sued ProAPIs in October 2025. hiQ ended in December 2022 with a consent judgment: a $500,000 payment and a halt to data collection. — [WebSearch summary citing nubela.co](https://nubela.co/blog/what-is-proxycurl-api-now-in-2026-im-the-founder/), [StartupHub](https://www.startuphub.ai/ai-news/startup-news/2025/the-1-linkedin-scraping-startup-proxycurl-shuts-down), [Yahoo Finance](https://finance.yahoo.com/news/linkedin-wins-legal-case-against-162510557.html) (secondary; no court filings read)
- France: on 5 Dec 2024, the CNIL fined KASPR €240,000, notably for collecting the contact details of LinkedIn members who had restricted their visibility. The data came through a paid Chrome extension, with about 160 million contacts. — [CNIL](https://cnil.fr/fr/aspiration-de-donnees-sanction-de-240-000-euros-lencontre-de-la-societe-kaspr); [EDPB news](https://www.edpb.europa.eu/news/news/2025/data-scraping-french-supervisory-authority-fined-kaspr-eu240-000_da)
- Apify LinkedIn post-search actors exist and are heavily used: [harvestapi/linkedin-post-search](https://apify.com/harvestapi/linkedin-post-search) ("No Cookies", 36,352 users, 9,768 in 30 days) and [apimaestro/linkedin-posts-search-scraper-no-cookies](https://apify.com/apimaestro/linkedin-posts-search-scraper-no-cookies) ($0.005 per item, 14,932 users). — [Apify Store API](https://api.apify.com/v2/store?search=linkedin%20posts%20search) (probe)

#### Facebook Groups
- Meta's Graph API v19.0 announcement (23 Jan 2024): "The Facebook Groups API is deprecated in v19 and will be removed from all versions in 90 days". This covered the publish_to_groups and groups_access_member_info permissions. — [Meta for Developers](https://developers.facebook.com/blog/post/2024/01/23/introducing-facebook-graph-and-marketing-api-v19/); impact reporting from [Gigazine](https://www.gigazine.net/gsc_news/en/20240206-meta-cuts-third-party-access-facebook-groups)
- An Apify-maintained Facebook Groups Scraper exists, with 45,177 users and 5,196 in the last 30 days — [apify/facebook-groups-scraper](https://apify.com/apify/facebook-groups-scraper) (probe of the Apify Store API).

#### Discord and Slack
- Discord's Terms ban "scraping our services without our written consent, including by using any robot, spider, crawler, scraper, or other automatic device", and "selling, licensing, or otherwise commercializing content or data obtained from our services". — [Discord Terms of Service](https://discord.com/terms)
- Syften lists "assorted Slack groups" among its sources (mechanism not stated) — [Syften](https://syften.com/). Sales Safari's authors note that many communities have moved to Slack, Discord, Telegram and Facebook Groups, and that forums are "far from dead". — [Alex Hillman, "Updating the Sales Safari System for 2023"](https://shorts.stackingthebricks.com/updating-sales-safari-2023/) (30 Dec 2022)

#### Niche professional forums (English), activity probes 2026-10-22
- LawnSite (lawn-care business owners): XenForo RSS works, with posts at 11:09 UTC that day — [probe](https://www.lawnsite.com/forums/-/index.rss).
- ContractorTalk (contractors): RSS works, with posts that day — [probe](https://www.contractortalk.com/forums/-/index.rss).
- Spiceworks Community (IT pros): runs on Discourse, `latest.json` works, active in Oct 2026 — [probe](https://community.spiceworks.com/latest.json).
- AccountingWEB UK "Any Answers": returned 403 with a bot challenge — [probe](https://www.accountingweb.co.uk/any-answers).
- Dentaltown message board and WebmasterWorld: both reachable (200), activity not gauged — [Dentaltown](https://www.dentaltown.com/messageboard), [WebmasterWorld](https://www.webmasterworld.com/).
- Syften's FAQ says it monitors "forums" in general — [Syften](https://syften.com/).

#### Quora
- `quora.com/about/tos` returned 403 to the automated fetch, so its terms were not read — [probe](https://www.quora.com/about/tos).

#### Stack Exchange
- Throttles: without a key, the probe returned `quota_max: 300` per day — [probe](https://api.stackexchange.com/2.3/info?site=webapps). With a key or an access token, the "default size [is] 10,000" per day. An IP sending more than "30 requests a second" is throttled, and clients must honor `backoff`. — [Stack Exchange API throttles](https://api.stackexchange.com/docs/throttle)
- The API terms require visible attribution to the Stack Exchange Network — [API Terms of Use](https://stackoverflow.com/legal/api-terms-of-use).
- In July 2024 the data dumps moved behind a login, with terms limiting use to personal and non-LLM projects. Critics argued this conflicts with CC BY-SA. Reports disagree on whether commercial use is barred. — [DevClass](https://devclass.com/2024/07/30/stack-exchange-restricts-access-to-dump-of-user-contributed-data-as-critics-complain-license-permits-reuse-for-any-purpose); [Archive Team wiki](https://wiki.archiveteam.org/index.php/Stack_Overflow)
- Software Recommendations SE, the "is there a tool" site: 23,384 questions in total, 9,973 unanswered. Its top-voted questions of the last 12 months score 8 or less, so activity is low. — [probe](https://api.stackexchange.com/2.3/info?site=softwarerecs)

#### YouTube Data API (comments)
- "Projects that enable the YouTube Data API have a default quota allocation of 100 search.list calls, 100 videos.insert calls, and 10,000 units per day combined for all other endpoints." `search.list` and `videos.insert` "have their own quota buckets", each defaulting to 100 per day. Quotas reset at midnight Pacific Time. — [YouTube quota costs](https://developers.google.com/youtube/v3/determine_quota_cost)
- `commentThreads.list`: "A call to this method has a quota cost of 1 unit". `maxResults` runs 1–100 (default 20). The `searchTerms` parameter limits results "to only contain comments that contain the specified search terms". — [commentThreads.list reference](https://developers.google.com/youtube/v3/docs/commentThreads/list)
- A YouTube Researcher Program exists for global API data — [YouTube quota costs](https://developers.google.com/youtube/v3/determine_quota_cost).

#### GitHub search API (feature requests by 👍)
- "For authenticated requests, you can make up to 30 requests per minute for all search endpoints except for the Search code endpoint". Unauthenticated: 10 per minute. "Up to 1,000 results for each search". Current API version: 2026-03-10. — [GitHub REST: Search](https://docs.github.com/en/rest/search/search)
- Probe: `q=is:issue is:open "feature request" in:title`, `sort=reactions-+1`, `order=desc` returned 390,674 issues. The top three: [hashicorp/terraform#2253](https://github.com/hashicorp/terraform/issues/2253) "feature request: inverse targeting / exclude" (1,539 👍), [microsoft/vscode#13953](https://github.com/microsoft/vscode/issues/13953) (1,509 👍), and [ValveSoftware/steam-for-linux#4924](https://github.com/ValveSoftware/steam-for-linux/issues/4924) (1,459 👍). An unauthenticated probe from the same IP was refused with "API rate limit exceeded". — [GitHub search API](https://api.github.com/search/issues?q=is:issue+is:open+%22feature+request%22+in:title&sort=reactions-%2B1&order=desc&per_page=3) (probe)

#### Product Hunt
- "The Product Hunt API must not be used for commercial purposes. If you would like to use it for your business, please contact us at hello@producthunt.com." The docs also mention rate limits and offer "faster access without rate limit" on request. — [Product Hunt API v2 docs](https://api.producthunt.com/v2/docs)

#### Indie Hackers
- `indiehackers.com` returned a 403 Cloudflare "Just a moment..." challenge to both curl and WebFetch — [probe](https://www.indiehackers.com/). Its posts on idea mining exist, for example "Want a SaaS idea that sells? Borrow it from 1-star reviews" — [Indie Hackers](https://www.indiehackers.com/post/want-a-saas-idea-that-sells-borrow-it-from-1-star-reviews-e1144022b7) (only the title was seen; fetch blocked).

### Inferences
| Source | Who writes there | Access, Oct 2026 | Cost | Terms | Automatable? | Best use |
|---|---|---|---|---|---|---|
| X | Founders, marketers, devs, some SMB owners | Official pay-per-use API ([docs](https://docs.x.com/x-api/getting-started/pricing)) | $0.005/post read, so 10,000 posts = $50 | API terms (not read here) | Yes, through the API | Vendor complaint monitoring ("@vendor" + "price", "cancel"), switching threads |
| LinkedIn | B2B decision-makers, consultants, French SMB pros | Manual only | Free | Scraping banned ([UA](https://www.linkedin.com/legal/user-agreement)); GDPR risk in the EU ([CNIL](https://cnil.fr/fr/aspiration-de-donnees-sanction-de-240-000-euros-lencontre-de-la-societe-kaspr)) | Not compliantly | Manual reading of posts and comments by practitioners in a niche |
| Facebook Groups | SMB owners, freelancers, trades, especially in France | Manual; join the group | Free | No API since 2024 ([Meta](https://developers.facebook.com/blog/post/2024/01/23/introducing-facebook-graph-and-marketing-api-v19/)) | Not compliantly | Sales Safari inside large groups |
| Discord / Slack | Tool communities, niche pros | Manual; membership | Free | Discord bans scraping ([terms](https://discord.com/terms)) | Not compliantly | Vendor and community servers' #feedback channels |
| Niche forums | Owners and operators in trades, IT, dental, SEO | RSS / Discourse JSON often open | Free | Per-forum terms (not read) | Often, through RSS | High-intent, operator-written threads |
| Stack Exchange | Devs, power users | Open API | Free (300/day keyless, 10k with key) | Attribution | Yes | Weak for B2B buying pain; webapps / superuser for workaround questions |
| YouTube comments | Users of paid tools (on tutorial videos) | Official API | Free quota | API ToS (not read) | Yes, about 10,000 `commentThreads` calls/day | Comments on vendor tutorials: "is there a way", "they removed", "too expensive now" |
| GitHub issues | Devs; self-hosted business-tool users | Official API | Free | GitHub ToS | Yes, 30 searches/min | Long-open, high-👍 feature requests in business-tool repos |
| Product Hunt | Makers, early adopters | API non-commercial | Free | Commercial use needs permission | Only with permission | Competitive scan, not buyer pain |
| Indie Hackers | Founders | Browser only (Cloudflare) | Free | Not read | No | Method write-ups; supply side |
| Quora | Mixed public | Browser only (403) | Free | Not read | No | Low priority |

- YouTube is underused and cheap. Ten thousand `commentThreads` calls a day, at up to 100 threads each, can cover the comments on most tutorial videos for a vendor category. Finding the videos needs `search.list` (100 calls a day) or curated channel lists.
- GitHub matters for B2B mainly where SMB operators file issues on self-hosted business software (ERP, invoicing, CRM). Developer-tool feature requests are dense but serve a developer buyer.

### Gaps
- The terms for the X API developer agreement, the YouTube API services, Meta's automated-data-collection rules and Quora were not read.
- The terms of LawnSite, ContractorTalk, Spiceworks and Dentaltown were not checked.
- Whether LinkedIn offers any official keyword search of public posts to ordinary developers was not verified.
- Product Hunt's rate-limit figures were not captured.
- Indie Hackers has no verified API.
- Slack: no compliant collection method beyond membership was found.

## 4. Review sites: access, terms, cost, and mining 1-3 star reviews of paid tools for switching signals

### Takeaway
The big B2B review sites (G2, Capterra and its siblings, TrustRadius, Trustpilot) block plain HTTP clients with bot challenges. G2's terms explicitly forbid automated extraction "whether or not such content is publicly accessible". Apify actors scrape them anyway for about $2–10 per 1,000 reviews, which is a terms-of-service risk. Openly accessible and automatable: the Shopify App Store (with a working star filter), WordPress.org (an API with rating breakdowns and support-thread counts, plus review RSS), and Google Play pages. Apple's legacy review RSS returned zero entries in every probe.

### Cited Findings

#### Access probes (2026-10-22)
- G2 product reviews page: 403 with a bot challenge — [probe](https://www.g2.com/products/hubspot-marketing-hub/reviews). Capterra: 403 challenge — [probe](https://www.capterra.com/p/61368/HubSpot-CRM/reviews/). TrustRadius: 403 challenge — [probe](https://www.trustradius.com/products/hubspot-crm/reviews). Trustpilot company page filtered to 1 star: 403 — [probe](https://www.trustpilot.com/review/www.shopify.com?stars=1).
- Shopify App Store reviews filtered with `ratings[]=1`: 200. Every star label on the page read "1 out of 5 stars", so the filter works. — [probe](https://apps.shopify.com/klaviyo-email-marketing/reviews?ratings%5B%5D=1)
- Google Play app page: 200 (about 210 KB of HTML) — [probe](https://play.google.com/store/apps/details?id=com.shopify.mobile&hl=en&gl=us). Chrome Web Store reviews URL: 302 redirect — [probe](https://chromewebstore.google.com/detail/grammarly-ai-writing-and/kbfnbcaeplbcioakkpcpgfkobkghlhen/reviews).
- Apple's legacy customer-reviews RSS (`itunes.apple.com/{cc}/rss/customerreviews/id={id}/sortby=mostrecent/json`) returned valid but empty feeds (0 entries) for four apps in the US and FR storefronts — [probe](https://itunes.apple.com/us/rss/customerreviews/page=1/id=371294472/sortby=mostrecent/json). Apple developer forum threads have reported the feed returning no entries for some apps before — [Apple Developer Forums](https://developer.apple.com/forums/thread/71769). No official deprecation notice was found.
- WordPress.org:
  - The plugin info API returns `ratings` by star, `num_ratings`, `support_threads` and `support_threads_resolved`. WooCommerce: 4,826 ratings (5★ 3,998; 4★ 197; 3★ 113; 2★ 108; 1★ 410), 132 support threads with 117 resolved, 7,000,000 active installs. — [probe](https://api.wordpress.org/plugins/info/1.2/?action=plugin_information&request%5Bslug%5D=woocommerce&request%5Bfields%5D%5Bsections%5D=0)
  - Plugin search by keyword works: "invoice" returned 1,996 plugins — [probe](https://api.wordpress.org/plugins/info/1.2/?action=query_plugins&request%5Bsearch%5D=invoice&request%5Bper_page%5D=3).
  - Each plugin's reviews have an RSS feed — [probe](https://wordpress.org/support/plugin/woocommerce/reviews/feed/).

#### Terms and official APIs
- G2 Terms of Use, section 9, "Prohibited Automated Access, Scraping, and Data Extraction": without "express prior written consent" you may not "access, collect, copy, scrape, harvest, cache, index, store, archive, or otherwise extract any content or data from the Site, including user reviews, reviewer identities or metadata, ratings ..." by "automated, programmatic, or mechanical means (including robots, spiders, crawlers, scrapers, headless browsers ...), whether or not such content is publicly accessible". — [G2 Terms of Use](https://legal.g2.com/terms-of-use)
- Trustpilot's developer site lists a "Business Units API (public)", a "Consumer API", a "Product Reviews API" and others — [Trustpilot Developers](https://developers.trustpilot.com/). Its access conditions were not captured. A scraping vendor says Trustpilot's terms bar unauthorized scraping and that official access needs a registered key — [webscraping.ai FAQ](https://webscraping.ai/faq/trustpilot-scraping/what-are-the-risks-of-trustpilot-scraping) (secondary).
- Google Play: "The Reply to Reviews API allows you to access feedback only for production versions of your app", meaning your own app — [Google Play Developer API](https://developers.google.com/android-publisher/reply-to-reviews).
- Apple's App Store Connect API has a Customer Reviews resource for developers' own apps — [Apple docs](https://developer.apple.com/documentation/appstoreconnectapi/customer-reviews).
- The Chrome Web Store API documentation covers publishing, not reading reviews — [Chrome for Developers](https://developer.chrome.com/docs/webstore/using-api).
- The terms of Capterra (Gartner Digital Markets) and TrustRadius could not be fetched (403 and 404). A scraping vendor says Cloudflare screens Gartner's pages — [WebSearch summary of scrape.do](https://scrape.do/industries/marketing/gartner-scraper/) (secondary).

#### Third-party scrapers and prices (Apify Store API probe, 2026-10-22; pay-per-event unless noted)
| Site | Actor (users) | Listed price |
|---|---|---|
| G2 | [powerai/g2-product-reviews-scraper](https://apify.com/powerai/g2-product-reviews-scraper) (775) | $0.00499 per item plus $0.09 per run start |
| G2 | [zen-studio/g2-reviews-scraper](https://apify.com/zen-studio/g2-reviews-scraper) (1,035); [factden/g2-reviews-scraper](https://apify.com/factden/g2-reviews-scraper), titled "Battlecards + Switching Data" (274) | tiered |
| Capterra | [epctex/capterra-scraper](https://apify.com/epctex/capterra-scraper) (855) | $0.0035 per item |
| Capterra | [getdataforme/capterra-reviews-scraper-bulk](https://apify.com/getdataforme/capterra-reviews-scraper-bulk) (276) | $0.01 per item |
| G2 + Capterra + Trustpilot | [zen-studio/software-review-scraper](https://apify.com/zen-studio/software-review-scraper) (517) | tiered |
| Trustpilot | [memo23/trustpilot-scraper-ppe](https://apify.com/memo23/trustpilot-scraper-ppe) (3,207; title "$0.65+") | add-ons: "pain-point-analysis" $0.05, "review-insights" $0.02 |
| TrustRadius | [epctex/trustradius-scraper](https://apify.com/epctex/trustradius-scraper) (108) | $0.002 per item |
| Shopify App Store | [jungle_synthesizer/shopify-app-store-scraper-2](https://apify.com/jungle_synthesizer/shopify-app-store-scraper-2) (279) | $0.002 per record plus $0.10 per start |
| Chrome Web Store | [easyapi/chrome-extension-scraper](https://apify.com/easyapi/chrome-extension-scraper) (42) | $0.00499 per item plus $0.09 per start |
| Apple App Store | [thewolves/appstore-reviews-scraper](https://apify.com/thewolves/appstore-reviews-scraper) (2,854) | "$0.10/1K Reviews" |
| Google Play | [thewolves/google-play-reviews-scraper](https://apify.com/thewolves/google-play-reviews-scraper) (2,008) | "$0.10/1K Reviews" |
| Google Play | [curious_coder/google-play-scraper](https://apify.com/curious_coder/google-play-scraper) (2,830) | $0.0003 per item |
| WordPress.org | [fatihtahta/wordpress-plugins-scraper](https://apify.com/fatihtahta/wordpress-plugins-scraper) (4) | "$4 / 1k" |
— source: [Apify Store API](https://api.apify.com/v2/store?search=g2%20reviews) (probe; Apify's own platform fees were not checked)

#### Techniques for mining 1-3 star reviews (practitioner and vendor write-ups)
- A Capterra-focused guide says to read the 1–3 star reviews of the top 5–10 products in a category. Flaws that recur across rival products reflect the category, not one unhappy user. Repeated "too expensive for small teams" complaints point to an opening for a leaner rival. Support pages and FAQs expose friction that never reaches reviews. Doing this by hand takes "8+ hours a week per category". — [BigIdeasDB: mine Capterra reviews](https://bigideasdb.com/mine-capterra-reviews-for-saas-ideas); [G2 feature-gap method](https://bigideasdb.com/turn-g2-reviews-into-saas-ideas); [negative reviews method](https://bigideasdb.com/find-saas-ideas-from-negative-reviews-g2-app-store). BigIdeasDB sells an idea database built from complaints; its guides disagree on whether to focus on 1★, 1–3★ or 3–4★.
- The paid Trustpilot actor sells a "pain-point-analysis" event, so vendors already package low-star mining as a product — [memo23/trustpilot-scraper-ppe](https://apify.com/memo23/trustpilot-scraper-ppe).

### Inferences
- **The cheapest compliant review mining is in marketplaces of add-ons, where the buyers are SMB merchants and site owners paying monthly.**
  - Shopify App Store: HTML is accessible and there is a star filter.
  - WordPress.org: the API exposes rating breakdowns and the share of support threads unresolved; the review RSS is open.
  - Google Play and Apple: these cover mobile SMB tools, Apple through paid actors.
- **Switching signals to search for inside low-star reviews of paid tools:**
  - "switched to / moved from / migrating to [rival]";
  - "price increase / doubled / renewal / per seat";
  - "support never responded / ticket";
  - "too complex / overkill for a small business / designed for enterprise";
  - "missing [feature] / still no [feature] after N years";
  - "had to export to a spreadsheet / use Zapier / hire someone".
  Count recurrence across the top 5–10 products. A complaint shared across several products is a category gap that a small add-on or a leaner product can serve.
- **Buyer type by site:**
  - G2, Capterra and TrustRadius: mid-market and SMB B2B software buyers and users. Reviews are often solicited by vendors, so they skew positive (see the J-shape in section 8).
  - Trustpilot: mixed consumer and B2B.
  - The Shopify App Store and WordPress.org: SMB merchants and site owners.
  - The Chrome Web Store: prosumers.
- Under G2's section 9, any automated collection of G2, including through an Apify actor, is a breach of contract. The compliant routes are manual reading or written permission from G2.

### Gaps
- Not read: the Capterra/GetApp/Software Advice, TrustRadius and Trustpilot terms, and the Shopify App Store's website terms.
- No official notice explains the empty Apple RSS results.
- Not verified: whether G2's review form records a "switched from" field (only an Apify actor title suggests "Switching Data"), and the share of incentivized reviews on G2 and Capterra.
- No independent study compares the quality of low-star B2B reviews as idea sources.

## 5. Public feature-request boards and vendor communities: finding long-standing, highly voted requests the vendor never built

### Takeaway
Atlassian's public Jira (jira.atlassian.com) is the gold standard. It allows anonymous REST/JQL queries sorted by votes, and returned 51,171 unresolved suggestions, the top ones with 2,400–2,850 votes, some open since 2003–2004. Discourse-based communities (Shopify Community, Make, Spiceworks) expose JSON search. Khoros communities (HubSpot) and inSided ones (Airtable) are behind bot protection or have no JSON, so they are browser-only. Salesforce IdeaExchange, Xero Product Ideas, Webflow Wishlist, the Microsoft Feedback Portal and Canny boards are live but were not machine-tested.

### Cited Findings
- **Atlassian, jira.atlassian.com:** an anonymous REST call with JQL `issuetype = Suggestion AND resolution = Unresolved ORDER BY votes DESC` returned 200 and a total of 51,171. The top five were:
  - [ID-240](https://jira.atlassian.com/browse/ID-240), "Ability to merge Atlassian accounts to a single account with secondary emails": 2,855 votes, created 2015-06-23, In Progress.
  - [JRACLOUD-4812](https://jira.atlassian.com/browse/JRACLOUD-4812), "Default values of system fields": 2,799 votes, created 2004-10-06, Future Consideration.
  - [JRASERVER-1391](https://jira.atlassian.com/browse/JRASERVER-1391), "Provide the ability to rename groups after creation": 2,627 votes, created 2003-03-03, Under Consideration.
  - [JRACLOUD-85694](https://jira.atlassian.com/browse/JRACLOUD-85694), "Ability to customize the fields shown on cards in team-managed projects": 2,462 votes, created 2018-11-21, Future Consideration.
  - [JRACLOUD-91595](https://jira.atlassian.com/browse/JRACLOUD-91595), "Milestones for Basic Roadmaps": 2,425 votes, created 2019-03-05, Under Consideration.
  — [probe](https://jira.atlassian.com/rest/api/2/search?jql=issuetype%20%3D%20Suggestion%20AND%20resolution%20%3D%20Unresolved%20ORDER%20BY%20votes%20DESC&fields=summary,votes,created,status&maxResults=5)
- **Shopify Community runs on Discourse** (assets from `discourse-cdn.com/shopifyforum`), and `latest.json` returns JSON — [probe](https://community.shopify.com/latest.json). `search.json?q="feature request" order:likes` returned threads such as "Revert one-page checkout back to 3-step checkout, and abandoned email flows..." (created 2023-10-03, 220 posts) and "Anyone else notice that the new returns system breaks all of shopify sales data" (2024-03-03, 123 posts). — [probe](https://community.shopify.com/search.json?q=%22feature%20request%22%20order%3Alikes)
- **Make (formerly Integromat) community:** Discourse with working `search.json`. Its threads include "Introducing: Make Idea Exchange" (2022-08-03) — [probe](https://community.make.com/search.json?q=%22feature%20request%22%20order%3Alikes).
- **Spiceworks Community:** Discourse, `latest.json` works — [probe](https://community.spiceworks.com/latest.json).
- **Airtable Community** runs on inSided (Gainsight): `top.json` returned 404 with inSided widget code — [probe](https://community.airtable.com/top.json?period=yearly).
- **HubSpot Community / Ideas** (Khoros): the LiQL API `community.hubspot.com/api/2.0/search` returned 403 behind a Cloudflare challenge — [probe](https://community.hubspot.com/api/2.0/search).
- **Live boards (200 responses, not machine-tested):** [Salesforce IdeaExchange](https://ideas.salesforce.com/) (title "IdeaExchange"), [Xero Product Ideas](https://productideas.xero.com/) ("Share and support customer ideas for Xero"), [Webflow Wishlist](https://wishlist.webflow.com/), [Microsoft Feedback Portal](https://feedbackportal.microsoft.com/feedback), [Canny's own board](https://feedback.canny.io/) — probes 2026-10-22. UserVoice's homepage now calls it a "Customer Intelligence Platform" — [probe](https://uservoice.com/).
- Canny's features include public voting boards — [ToolRadar](https://toolradar.com/tools/canny/alternatives). A one-star review mentions a highly voted request on Canny's own public roadmap — [WebSearch summary of Aloa / Software Advice](https://aloa.co/blog/canny-review-customer-feedback-made-easy) (secondary).

### Inferences
- **Recipe for "voted for years, never built" requests:**
  1. On Jira-style public trackers, filter on unresolved, add `created <= -3y`, keep statuses meaning "not soon" ("Future Consideration", "Under Consideration", "Not Being Considered"), and order by votes.
  2. On Discourse, use `search.json?q=<category terms> order:likes` or `/top.json?period=all` on the ideas category, then keep the threads where staff last replied long ago or with "not planned".
  3. On idea portals (Salesforce, Xero, HubSpot, Canny), sort by "Top" in the browser and filter by status.
  4. Check the vendor's marketplace (Atlassian Marketplace, Shopify App Store, Salesforce AppExchange, Xero App Store) for add-ons that already fill the gap. A strong gap with no add-on, or only poorly rated ones, is the target.
- **Money attached:** voters on these boards are by definition paying customers of the vendor or its trialists, and an add-on has a ready distribution channel, the vendor's marketplace. That makes these boards high-signal for the "small add-on" route.
- **Signal decay:** the oldest requests (2003–2004) often have no add-on because they need platform internals. Check feasibility through the vendor's extension API before treating a vote count as demand.

### Gaps
- Not verified: the sort and status vocabularies of Salesforce IdeaExchange, Xero, Canny and Productboard portals; whether UserVoice still hosts public forums; and the public feature boards of Notion and Airtable.
- No source quantifies how often marketplace add-ons succeed by filling highly voted gaps.
- Productboard portals were not tested.

## 6. French-language sources: where French SMB owners, freelancers, accountants, trades and professionals discuss tools and admin pains

### Takeaway
French B2B talk is not on Reddit: French B2B subreddits are missing or tiny. It lives on LinkedIn and Facebook groups (the largest freelance and entrepreneur groups have 46k–103k members, per an Aug 2026 list), on a few still-active web forums (WebRankInfo, Developpez.net, Comment Ça Marche, plus trade and accounting media with discussion spaces such as Compta-Online), and in vendor communities. The JDN forum is gone. The e-invoicing reform, in force since 1 Sept 2026, is a live, money-attached admin pain for French companies.

### Cited Findings
- **Reddit (FR), from Arctic Shift metadata:** r/france 2,292,429 subscribers; r/immobilier 85,602; r/developpeurs 38,548; r/Comptabilite 73. No subreddit was found for r/AutoEntrepreneur, r/Entrepreneur_fr, r/freelance_fr or r/EntrepreneurFrancais; the r/vosfinances lookup failed with 422. — [probe](https://arctic-shift.photon-reddit.com/api/subreddits/search?subreddit=developpeurs)
- **Web forums (activity probes, 2026-10-22):**
  - WebRankInfo forum (SEO, webmasters, site owners): RSS active, with the latest posts at 10:29 and 10:27 UTC that day, for example "Avis sur le design de mon annuaire d'outils IA en français" — [probe](https://www.webrankinfo.com/forum/forums/-/index.rss).
  - Developpez.net (developers and IT professionals): RSS active, posts on 21–22 Oct 2026 — [probe](https://www.developpez.net/forums/external.php?type=RSS2).
  - Comment Ça Marche forums: active, with 46 October-2026 dates on the forum index. Mostly IT support, plus a "Bureautique" section with threads like "Trier une colonne sur excel numéro de compte comptable" — [probe](https://forums.commentcamarche.net/forum/).
  - JDN forum: `journaldunet.com/forum/` returned 404 "Page non trouvée" — [probe](https://www.journaldunet.com/forum/).
  - Excel-Downloads (a French Excel help forum): RSS answered with a "Checking your browser" anti-bot page, so activity was not verified — [probe](https://excel-downloads.com/forums/-/index.rss).
  - Pragmatic Entrepreneurs (a French bootstrapper forum on Discourse; per Maddyness, attributed to Camille Roux, co-founder of Human Coders): about 4,347 topics across its categories, with roughly 11 new topics in the last month. The largest categories are Entrepreneuriat (819 topics), Juridique (716), Comptabilité (533), Feedback (350) and Marketing (283). Its JSON API is open. — [probe](https://forum.pragmaticentrepreneurs.com/categories.json); [Maddyness](https://www.maddyness.com/?p=121570)
  - Compta-Online calls itself a "Média communautaire". It has "Discussions" spaces for Professionnels, Entrepreneurs, Particuliers and Étudiants, plus a "Logiciels" section, and published an e-invoicing white paper on 18 Oct 2026. Forum thread activity could not be gauged from the page. — [WebFetch of compta-online.com/forums](https://www.compta-online.com/forums). Semrush estimated about 328,000 site visits in Oct 2025. — [Semrush FR](https://fr.semrush.com/website/compta-online.com/overview) (estimate, a year old)
  - A paid forum at startbusinessinfrance.com was recommended in an AccountingWEB thread, for anglophones running businesses in France — [AccountingWEB](https://www.accountingweb.co.uk/node/63041) (undated).
- **Facebook groups, from a list published 6 Aug 2026 (approximate member counts):**
  - "Entrepreneurs & Freelances FR": about 102,700, "very high" activity.
  - "Entrepreneurs et freelances": about 81,600.
  - "Indépendants et Freelances du Web": about 47,900.
  - "Freelance en France": about 46,100.
  - "Mission freelance en start-up": about 42,300.
  - "Freelancers En France": about 22,600, private.
  - "Aide & Entraide Auto/Micro-entrepreneurs": about 6,200, private.
  - "Le Cercle des Indépendants" (very small businesses, craftspeople, freelancers): about 2,400.
  — [Munci, 6 Aug 2026](https://www.munci.org/top-10-des-groupes-facebook-pour-freelances-en-2026/)
- **Facebook groups, from a list dated 4 Sept 2023:**
  - "La communauté des auto-entrepreneurs": 61,000, run by Portail Auto-Entrepreneur.
  - "Entraide auto/micro-entrepreneurs": 54,000, linked to HelloMyBusiness. Members discuss providers, software reviews, legal and accounting questions.
  - "French Startups": 35,400. "Le journal du community manager": 38,000. "Growth Hacking France": 19,000. "SEO France": 8,000. "Facebook Ads France": 5,500.
  - "Artisans et Auto-entrepreneurs": 5,400.
  — [Tool-Advisor, 4 Sept 2023](https://tool-advisor.fr/blog/groupe-facebook-entrepreneur/). The "Entraide" group's size conflicts between the two lists: 54,000 versus about 6,200, possibly different groups with similar names.
- **Vendor communities and review sites in French:** a French Sage 100 Comptabilité & Gestion forum on the Sage Community Hub — [Sage Community Hub FR](https://communityhub.sage.com/fr/sage-100/leaders/top-participantes-du-mois); GetApp has French-language listings — [getapp.fr example](https://www.getapp.fr/software/108461/canny); Appvizer is live, describing itself as "Média & Comparateur de Logiciels pour les Professionnels" — [probe](https://www.appvizer.fr/).
- **A live admin pain:** "La réforme de la facturation électronique entre entreprises est entrée en vigueur le 1er septembre 2026". All companies must now receive e-invoices; large companies and mid-caps (ETI) must also issue them and transmit e-reporting data. — [economie.gouv.fr](https://www.economie.gouv.fr/tout-savoir-sur-la-facturation-electronique-pour-les-entreprises) (page dated 12/10/2026)
- **Legal context for collecting French data:** the CNIL's €240,000 fine against KASPR (Dec 2024) for LinkedIn contact scraping — [CNIL](https://cnil.fr/fr/aspiration-de-donnees-sanction-de-240-000-euros-lencontre-de-la-societe-kaspr).

### Inferences
- **Priorities for French SMB pain mining:**
  1. Large Facebook groups for freelancers and micro-entrepreneurs, read manually: the densest open discussion of tools, URSSAF, invoicing and accounting.
  2. LinkedIn comment threads of French accountants and SMB consultants, read manually. Accountants and payroll providers relay their clients' admin pains.
  3. Compta-Online and vendor communities (Sage, and likely the accounting-software communities), where paid-tool users ask how to do X.
  4. Trades: regional artisan Facebook groups. No large open trade forum was verified.
  5. Excel and office forums (CCM Bureautique, Excel-Downloads), where spreadsheet workarounds reveal unserved needs.
- The e-invoicing rollout gives a time-boxed window. Micro-businesses and SMEs now receive e-invoices and will later have to issue them, a deadline not verified here. Expect "quelle plateforme", "trop cher", "mon logiciel ne gère pas" discussions with money attached.
- Automatable French sources are few: the RSS of WebRankInfo and Developpez, the Discourse JSON of Pragmatic Entrepreneurs, and Comment Ça Marche pages. The highest-value French sources, Facebook and LinkedIn, are manual only.

### Gaps
- Not researched or verified: professional associations (CAPEB, CPME, U2P, FNAE, Ordre des experts-comptables) and whether they host public discussion spaces or publish pain surveys; also the regional CCI and BPI communities.
- Activity was not verified for Excel-Downloads (anti-bot) or Compta-Online's discussion threads.
- No data was found on French SMB use of LinkedIn as opposed to Facebook for tool discussions.
- Trustpilot FR and Capterra FR were not probed separately.
- French-language Discord and Slack communities (for example freelance collectives) were not identified.
- The obligation dates for SMEs and micro-businesses to issue e-invoices were not captured from the official page.

## 7. Phrase patterns, in English and French, that signal pain with money attached, and evidence on which work best

### Takeaway
No published study ranks these phrases by buying conversion. Probe counts show the generic money phrases ("we pay", "I would pay", "alternative to", "too expensive") are high-volume and low-precision in general communities. The rare, behavior-describing phrases ("hired someone to", "manually every", "is there a tool", "we're paying X for") carry more intent per hit. Practitioners and tools pair phrases with a community filter, a domain noun and an AI or human intent check; GummySearch's taxonomy, for instance, separated "Pain & Anger" from "Solution Requests" and "Money Talk".

### Cited Findings
- Volume in HN comments over the last 365 days, and the precision samples, are in section 2. "alternative to" had 3,931 hits and "too expensive" 2,561, against 42 for "manually every" and 1 for "hired a VA". The newest "we pay" and "I would pay" hits were off-topic or consumer. — [HN Algolia probe](https://hn.algolia.com/api/v1/search?query=%22we%20pay%22&tags=comment&advancedSyntax=true&numericFilters=created_at_i%3E1761130000)
- In Arctic Shift's Reddit comment search, `body="we pay"` in r/Bookkeeping returned comments about rates and referral fees ("my rate was $205 an hour"; "I pay out 10% referral fees"). That is money talk, but not always tool spend. The search does token rather than phrase matching. — [probe](https://arctic-shift.photon-reddit.com/api/comments/search?subreddit=bookkeeping&body=%22we%20pay%22&limit=100)
- **French probe** on Pragmatic Entrepreneurs (Discourse `search.json`; first-page post counts, where 50 is the page cap):
  - "trop cher" 50+; "à la main" 50+; "abonnement" 50+; "expert-comptable" 50+; "existe-t-il" 49; "perte de temps" 44; "alternative à" 21; "fichier Excel" 21; "tableur" 15; "je paierais" 12.
  - The samples included workarounds with money attached: subscriptions "générés en back-office (manuellement) grâce à Stripe"; accounting done by downloading eBay files into Excel; a search for "alternative à" to cut business phone costs abroad.
  - The "je paierais" sample was about company valuation, which is noise.
  — [probe](https://forum.pragmaticentrepreneurs.com/search.json?q=%22alternative%20%C3%A0%22)
- **GummySearch's subreddit pages** labeled themes such as "Pain & Anger", "Solution Requests" and "Money Talk", each with counts and example posts. These pages remain visible after the closure, but their data may be stale. — [gummysearch.com/r/extremelyinfuriating](https://gummysearch.com/r/extremelyinfuriating/), [gummysearch.com/r/needadvice](https://gummysearch.com/r/needadvice) (via a WebSearch summary)
- **Buying-intent tools** treat "alternative to" (with a competitor's name), "can anyone recommend" and "looking for a tool" as buying signals, add switching language, and score intent with AI. They publish no independent conversion data. One builder reports about 100 leads a week, with a human approving every reply. — [WebSearch summary of Apify lead-finder actors and vendor pages](https://apify.com/logiover/reddit-lead-finder) (vendor content)

### Inferences
- **Pattern library**, ordered by expected intent per hit. Always combine a pattern with a buyer-dense community and a domain noun, then confirm with a human read.
  1. **Spend already happening (strongest).**
     - EN: "we pay $", "we're paying", "costs us", "per seat", "per month for", "our plan", "renewal", "they raised the price", "price increase".
     - FR: "on paie", "ça nous coûte", "par mois", "abonnement", "HT/mois", "par utilisateur", "augmentation de prix", "renouvellement".
  2. **Paid human workaround.**
     - EN: "hired a VA to", "hired someone to", "our bookkeeper does", "outsourced", "pay an intern".
     - FR: "j'ai embauché", "on a pris un(e) assistant(e)", "mon expert-comptable fait", "on sous-traite", "un stagiaire qui".
  3. **Unpaid manual workaround.**
     - EN: "spreadsheet", "Google Sheets", "manually every week", "copy-paste", "Zapier hack", "macro", "every month I have to".
     - FR: "à la main", "manuellement", "tableur", "fichier Excel", "copier-coller", "chaque semaine je dois", "perte de temps".
  4. **Switching and alternatives.**
     - EN: "switching from", "moving off", "cancelled", "alternative to", "replacement for", "migrating".
     - FR: "alternative à", "changer de logiciel", "quitter", "résilier", "remplacer".
  5. **Tool search.**
     - EN: "is there a tool", "is there an app", "looking for a tool", "any recommendations for", "what do you use for".
     - FR: "existe-t-il un outil", "vous utilisez quoi pour", "quel logiciel", "une solution pour", "je cherche un outil".
  6. **Hypothetical willingness to pay (weakest).**
     - EN: "I'd pay for", "I would pay", "happy to pay", "take my money".
     - FR: "je paierais", "je serais prêt à payer".
     - These state future behavior, which the Mom Test discounts (section 8).
- **Context filters that raise precision:**
  - A role or size marker: "my clients", "our team of 8", "my agency", "our practice", "cabinet", "TPE", "PME", "artisan".
  - A named incumbent vendor.
  - A currency figure.
  - Recency: the last 12–24 months.
  - Recurrence: the same pain in at least three independent threads or sources.
- In tools with token-based search (Arctic Shift, Discourse), run the broad query, then apply the exact phrase as a local regex before counting.

### Gaps
- No study measures how often each phrase converts to a paying customer, in any language.
- No French-specific evidence on pattern efficacy was found; the French list is inferred.
- Precision was spot-checked on three samples per pattern, not measured statistically.

## 8. Signal quality: complainers versus buyers, selection bias, and how practitioners separate a real buying pain from venting

### Takeaway
Public complaints are a biased sample. Review distributions are J-shaped because extreme reviewers self-select. Most community members never post (the 90-9-1 pattern). Reddit and HN users are skewed demographically. Practitioners separate buying pain from venting by behavior: past spend, existing workarounds, switching, a buyer who fits the target, and threads with many substantive replies. Stated willingness to pay and complaints alone count as weak evidence.

### Cited Findings
- Hu, Pavlou and Zhang attribute the J-shaped (bimodal, positively skewed) distribution of online reviews to self-selection: people who buy already lean positive, and people with extreme views post more. Average stars therefore mislead. In a lab test where everyone rated the same product, ratings formed a single peak. — [Overcoming the J-shaped Distribution of Product Reviews, CACM 2009 (SMU repository)](https://ink.library.smu.edu.sg/sis_research/780); [MIS Quarterly 2017 follow-up](https://ink.library.smu.edu.sg/sis_research/8012); [2007 manuscript](https://archive.nyu.edu/bitstream/2451/14951/2/usedbook1.pdf)
- A live example: WooCommerce's WordPress.org ratings are 5★ 3,998; 4★ 197; 3★ 113; 2★ 108; 1★ 410. One-star reviews outnumber two- and three-star reviews combined. — [WordPress.org plugin API probe](https://api.wordpress.org/plugins/info/1.2/?action=plugin_information&request%5Bslug%5D=woocommerce&request%5Bfields%5D%5Bsections%5D=0)
- Participation inequality ("90-9-1"), from Jakob Nielsen's 2006 Alertbox: about 90% of community members lurk, 9% contribute occasionally and 1% produce most content. Variants for blogs (95-5-0.1) and Wikipedia (more than 99% lurkers) appear in secondary write-ups. — [P2P Foundation wiki](https://wiki.p2pfoundation.net/Participation_Inequality); [reproduction of the 2006 column](https://churbuck.com/2006/10/31/) (secondary; nngroup.com was not fetched)
- Reddit reaches 26% of U.S. adults, according to Pew's "Americans' Social Media Use 2025" (5,022 adults surveyed Feb–June 2025) — [Tubefilter](https://www.tubefilter.com/2025/11/21/pew-research-center-us-social-media-report/). Pew's June 2025 data: 29% of men versus 23% of women use it — [Statista](https://www.statista.com/statistics/261765/share-of-us-internet-users-who-use-reddit-by-gender/) (secondary relays of Pew).
- The Mom Test (Rob Fitzpatrick), as summarized: talk about the person's life rather than your idea; ask about specifics in the past, not opinions about the future; listen more. Compliments and polite enthusiasm are weak evidence. Real signal is commitment and advancement that costs the customer time, money or reputation, such as a follow-up meeting, a pilot, a referral or a letter of intent. — [Sachin Rekhi's primer](https://www.sachinrekhi.com/the-mom-test-rob-fitzpatrick); [Unusual Ventures, 31 Oct 2024](https://www.unusual.vc/rob-fitzpatricks-mom-test/) (summaries, not the book)
- Sales Safari (Amy Hoy and Alex Hillman, about 2010; reworked in 2015 and updated for 2023) is passive observation of real conversations in the communities where the audience gathers. The 2023 update says the method has not changed, but communities have spread to Slack, Discord, Telegram, Facebook Groups and TikTok. — [Alex Hillman, 30 Dec 2022](https://shorts.stackingthebricks.com/updating-sales-safari-2023/); [Stacking the Bricks podcast ep42](https://stackingthebricks.com/podcast/ep42-what-is-sales-safari-with-eteinne-garbugli/). In summaries, notes split into pains, jargon, worldview and recommendations. — [WebSearch summary of Sales Safari sources](https://swipefiles.com/sales-safari)
- Commoncog's "Speedrunning the Skill of Demand" thread (Cedric Chin, 14 Mar 2025, replies to 30 Nov 2025):
  - Identify the pain before choosing a format.
  - Existing paying customers and competitors' customers are "perhaps higher signal" interview subjects.
  - Prefer threads with many substantive replies from the target audience over "drive-by questions". Amy's workshop used a 60-post thread.
  - Expect less chatter in low-interest categories, where buyers "satisfice".
  - When demand is absent, "don't fight it — just move on".
  — [Commoncog forum](https://forum.commoncog.com/t/speedrunning-the-skill-of-demand-commoncog/2584)
- Practitioner blogs rank paid workarounds, outside help, spreadsheets and stacked-up tools as stronger evidence than stated interest. They count a pain recurring in similar words across about ten people as meaningful, and outrank polite interest with acts such as a request for a quote or a second meeting with the budget holder. — [wpreset.com](https://wpreset.com/5-proven-ways-to-validate-a-startup-idea-before-building-a-product/); [Stackmatix](https://www.stackmatix.com/blog/how-to-validate-a-startup-idea) (blog-level evidence)
- An Indie Hackers post, "A complaint is not a SaaS idea — the workaround is the real signal", argues that workarounds and repeat forum complaints expose urgency. A reply cautions that a tolerable workaround makes switching harder. Another IH founder reports that only about 2–5% of those who expressed interest ended up paying. — [Indie Hackers post](https://www.indiehackers.com/post/a-complaint-is-not-a-saas-idea-the-workaround-is-the-real-signal-21d696f15b) (read through a search summary; the page blocks automated fetches)
- Commercial validation of this approach: GummySearch's tooling for the method reached "over 135,000 founders, marketers, and investors" before closing for licensing reasons — [GummySearch: final chapter](https://gummysearch.com/final-chapter).

### Inferences
- **Six checks that separate a buying pain from venting**, each answerable from public text before any conversation:
  1. **Spend now:** the poster names a tool, a price, a seat count, a freelancer or an employee already paid to handle it.
  2. **Behavior:** they describe a workaround they already run (a spreadsheet, a macro, Zapier, a VA, manual weekly steps), not just a feeling.
  3. **Switching motion:** they cancelled, are evaluating alternatives, or name the trigger (a price hike, a removed feature, a support failure).
  4. **Fit:** the poster matches the target buyer by role, company size and geography. Check profile history where visible.
  5. **Recurrence:** the same pain appears across at least three independent communities or sources, or carries votes (JAC, Discourse likes, Canny votes).
  6. **Recency and persistence:** recent posts on an old pain (requests open for years) beat a one-off spike after an outage.

  "Pain & Anger" without 1–3 is venting. "Solution Requests" plus "Money Talk" with 4–5 is a candidate worth outreach.
- **Correcting for selection bias:**
  - Weight 2–3 star reviews of paid tools: they are written by people who stayed long enough to know the product.
  - Read low-star reviews as signs of where things fail, not of how often.
  - Remember lurkers: the 1% who post skew vocal, technical and young. Non-posting buyers, especially trades and French micro-businesses, need direct contact, which the Commoncog thread also advises for low-interest categories.
- **The public text only nominates candidates.** The test is a behavior ask: a pre-order, a paid pilot, a call with the budget holder. That matches the Mom Test's commitment and advancement, and the factory's 48-hour test.

### Gaps
- No peer-reviewed study was found linking public complaint posts or low-star reviews to later purchase of an alternative.
- Primary pages were not fetched for: the 2006 Nielsen column (nngroup.com), Pew's full tables on Reddit by age and education, and the original text of The Mom Test.
- The Indie Hackers figures are anecdotes read through a search summary.
- No evidence was found on the share of reviews that are vendor-incentivized on G2 or Capterra, or on how that changes the content of low-star reviews.
