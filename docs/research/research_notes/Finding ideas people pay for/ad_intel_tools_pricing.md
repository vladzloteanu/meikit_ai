# Ad-intelligence tools for spotting advertisers whose spend is rising (France/EU first, US second)

Pages read 2026-10-22 by the helper of the ad-spend researcher; saved verbatim by the coordinator
after the parent run stopped on an API session limit. No files written by the helper, no API keys
used, nothing spent. SpyFu's pricing pages blocked automated reads (403) and PiPiAds' pricing page
loads its prices by JavaScript, so neither page could be read.

**Legend.** [V] = read on the vendor's own page today. [3P] = third-party page, with its date when
known. [C] = vendor claim. [U] = not verified. Prices are in USD unless marked; "annual" means a
per-month price billed yearly.

## What matters most

- **Spend estimates under 100 EUR are rare.** Tools that estimate spend from a panel or a model
  start at $129/mo (AdClarity: one market, one channel, three months of history) and rise to
  enterprise contracts.
- **The cheap "ad spy" tools don't estimate spend.** They show creatives, days running and live-ad
  counts. Gethookd says so outright: "We do not estimate a brand's revenue or invent a spend
  figure" ([V](https://www.gethookd.ai/)).
- **The best cheap signal for France/EU is Meta's own transparency data.** For every ad delivered
  in the EU, Meta's Ad Library publishes an EU reach figure (`eu_total_reach`), whatever the ad's
  category. Spend and impressions stay political-only
  ([Meta reference](https://developers.facebook.com/docs/graph-api/reference/archived-ad/),
  [ppc.land](https://ppc.land/ads-library/),
  [Zernio docs](https://docs.zernio.com/platforms/meta-ads/ad-library)). [U] Access needs a Meta
  developer account with identity confirmation.

## Main tools

### Semrush (Advertising Research / Shopping ads; Traffic & Market)
- **What it estimates:**
  - The Advertising toolkit covers Google Ads "Positions, Position Changes, Competitors, Ad
    Copies" and "Google Shopping ads research" ([V](https://www.semrush.com/pricing/advertising/)).
  - [U] The paid "traffic cost" metric was not re-checked on a Semrush page.
  - Traffic & Market splits traffic into Paid Search, Paid Social and Display Ads, and gives no ad
    spend figure ([V, undated](https://www.semrush.com/kb/1121-semrush-traffic-and-market)).
  - AdClarity, sold inside Semrush, is presented as giving competitors' "ads spend and impression"
    [C] ([Semrush news](https://www.semrush.com/news/271381-adclarity-advertising-intelligence-get-insights-on-competitors-digital-ads-spend-and-impression/)).
- **Coverage:** France is one of nine core markets with history from January 2012 (an SEO-data
  statement); the paid-keyword archive also starts in 2012, no per-country breakdown
  ([KB 64](https://www.semrush.com/kb/64-historical-data)).
- **Price:** Advertising toolkit Base €94.94/mo, Pro €210.98/mo, both billed yearly
  ([V](https://www.semrush.com/pricing/advertising/)); a Semrush KB lists $99 and $220 billed
  annually ([KB](https://www.semrush.com/kb/1551-pricing-and-plans)); only Pro adds AdClarity.
  Traffic & Market Pro $289/mo ([V](https://www.semrush.com/kb/1121-semrush-traffic-and-market)).
  SEO + AI Search plans: SEO €134/mo (€112.52 annual), Starter €190 (€158.40), Pro+ €286 (€238),
  Advanced custom ([V](https://www.semrush.com/prices/)).
- **API:** the Standard API is "an add-on to the Business tier" ([V, undated](https://www.semrush.com/kb/5-api)),
  which conflicts with today's pricing page (API on Advanced, custom price)
  ([V](https://www.semrush.com/prices/)); a competitor's blog says Advanced is $549/mo with zero
  units ([SE Ranking](https://seranking.com/blog/semrush-api-alternatives/)). Domain Ad History in
  the API costs 100 units per line, last 12 months
  ([V](https://developer.semrush.com/api/v3/seo/domain-reports/)). Base includes "Unlimited Google
  Ads exports".
- **Free tier:** 10 reports/day, 7-day trial ([V](https://www.semrush.com/prices/)).
- **Accuracy:** one blog test on a single account: about $5k/mo estimated against $13.8k/mo actual
  ([Jumpfly](https://www.jumpfly.com/blog/are-competitive-spying-tools-worth-it-for-ppc/), undated).

### Similarweb
- **What it estimates:** "Ads Intel Suite": paid search, display & social, AI ads, publishers
  ([V](https://www.similarweb.com/corp/pricing/)). PPC spend = paid-search visits × paid keywords ×
  CPC by country, only above 5,000 paid-search visits in the period
  ([support](https://support.similarweb.com/hc/en-us/articles/360018815797-PPC-Spend)); display
  impressions and spend modelled from traffic, CPM and CTR
  ([support](https://support.similarweb.com/hc/en-us/articles/24435120044957-Ad-Intelligence-Overview)).
- **Coverage:** 100+ countries, up to 37 months.
- **Price:** not on the vendor page; a tracker's snapshot of 2026-09-28: Competitive Intelligence
  $199/mo ($125 annual); +SEO & AEO $399 ($333); +Ads $649 ($542)
  ([3P](https://pricingsaas.com/companies/similarweb)). APIs with custom Business packages.

### SpyFu
- Google Search ads only: keywords, ad history, budget estimates; 32 countries incl. France, Germany,
  Spain, Italy, Netherlands, Belgium, UK, US
  ([V, 2026-03-19](https://help.spyfu.com/en/articles/2968557-which-countries-does-spyfu-collect-data-in)).
- **Price** (vendor pages 403; third-party, unverified): Basic $39, Professional $79
  ([3P, Aug 2025](https://www.bestever.ai/post/spyfu-pricing)); Basic $39, "Pro + AI" $119, Team $249,
  25 % off yearly ([3P, 2026](https://www.trendtrack.io/blog-post/spyfu-review)). Historical data
  only on Pro + AI and Team ([V, 2026-02-12](https://help.spyfu.com/en/articles/5569689-more-answers-about-our-pricing-and-plans)).
  API on the mid tier, 10k rows/mo, $0.50 per extra 1,000 [U].
- **Accuracy:** inherits Keyword Planner errors
  ([V](https://help.spyfu.com/en/articles/3048130-data-accuracy-what-to-do-if-estimates-seem-off));
  single-account test about $6k/mo against $13.8k actual
  ([Jumpfly](https://www.jumpfly.com/blog/are-competitive-spying-tools-worth-it-for-ppc/)); a 2007
  critique found up to 10× errors ([old](https://blog.minethatdata.com/2007/04/spyfu-inaccuracies-rimm-kaufman-group.html)).

### Sensor Tower Ad Intelligence (ex-Pathmatics)
- Spend, impressions and share of voice across Facebook, Instagram, YouTube, TikTok, X, Snapchat,
  LinkedIn, display, video, programmatic, OTT/CTV; no search ads
  ([V](https://sensortower.com/pathmatics-connect)). US, CA, UK, DE, IT, ES, FR, AU plus select
  regions ([V](https://sensortower.com/pathmatics-dashboard/)). Price not published (demo only).
  Opt-in panel + crawlers + ML [C]; no independent audit found; G2 reviewers flag accuracy and
  coverage ([G2](https://g2.com/products/pathmatics-by-sensor-tower/reviews)).

### MediaRadar (+ Vivvix)
- MediaRadar acquired Vivvix (Kantar's North American ad intelligence), announced 2023-11-02
  ([Kantar](https://www.kantar.com/north-america/company-news/mediaradar-acquires-vivvix-kantars-north-american-ad-intelligence-business)).
  France coverage not found [U]. About $19k–97k a year, median ~$25k, from 13 deals
  ([Vendr 3P](https://www.vendr.com/marketplace/mediaradar)).

### Adbeat
- Standard $249/mo (90 days of history), Advanced $399/mo (one year, country filter), Enterprise
  "Call" (three years, "ad spend estimates") ([V](https://www.adbeat.com/pricing)). Display,
  programmatic and native (Taboola, Outbrain...), no Meta; 35 countries incl. France. Free Basic.

### AdClarity (BIScience)
- Basic $129/mo (one market, one channel, three months), Advanced $289, Team $349, Enterprise
  (52 markets, history to 2018); 7-day trial ([V](https://www.adclarity.com/pricing/)). Panel of
  25–30M opt-in users [C, figures conflict]. CTV in 20 markets incl. France since June 2026
  ([trade](https://www.advanced-television.com/2026/06/15/adclarity-expands-ctv-ad-intelligence-to-20-markets/)).

### Creative "spy" tools without spend estimates
- **BigSpy:** free (Facebook, 10 searches/day); Starter $69 ($49 annual); Growth $159 ($119) adds
  Google, YouTube, X, TikTok; Scale $399; Ultimate $499 ([V](https://bigspy.com/pricing)).
- **AdSpy:** Facebook/Instagram, $149/mo [C] ([V](https://adspy.com/)).
- **PowerAdSpy:** $69–399/mo ($27–119 annual); "Estimated Ad Budget" on the top two tiers, method
  unpublished [U] ([V](https://poweradspy.com/pricing/)).
- **Foreplay:** $59/mo ($49 annual) to $459; API and MCP from Workflow ($175); Meta, TikTok,
  LinkedIn; sorts by time running ([V](https://www.foreplay.co/pricing)).
- **Minea:** $49–199/mo; Facebook ads ([V](https://www.minea.com/pricing)).
- **PiPiAds:** $49/mo (30k credits), $99 (100k) per search snippets
  ([V-snippet](https://www.pipiads.com/pricing)); TikTok and Facebook.
- **Atria:** Core $129/mo annual, REST API 1,200 calls/mo ([V](https://www.tryatria.com/pricing)).
- **Gethookd:** Meta only, days running and live-ad counts, no spend; $19–129/mo
  ([V](https://www.gethookd.ai/)).

### API-first and EU-specific
- **Trendtrack:** about $34, $62 or $111/mo billed yearly; "reach and budget (spend) estimates for
  EU ads, based on Meta's transparency disclosures", daily per tracked EU brand (2, 10 or 20
  brands); API and MCP from Pro ([V](https://www.trendtrack.io/pricing)). Spend method not
  published [U].
- **Apify Facebook Ads Scraper:** $3.40–5.80 per 1,000 ads; `isDetailsPerAd` adds EU total reach,
  age and gender by country, payer and beneficiary ([V](https://apify.com/apify/facebook-ads-scraper)).
- **ScrapeCreators:** Facebook, TikTok, Google and LinkedIn ad-library APIs; $47 for 25k credits
  ([V](https://scrapecreators.com/)).
- **Adyntel:** Meta, Google Transparency, LinkedIn ("impression counts"), TikTok; $44/mo for 5k
  credits ([V](https://adyntel.com/)).
- **SerpApi Google Ads Transparency Center API:** per creative `first_shown`, `last_shown`,
  `total_days_shown`; filters by region, platform (SEARCH, YOUTUBE, SHOPPING, PLAY, MAPS), date;
  no impressions or spend; 250 free searches/month, $25 for 1,000
  ([V](https://serpapi.com/google-ads-transparency-center-api), [pricing](https://serpapi.com/pricing)).
- **Kalodata / FastMoss (TikTok Shop sales estimates):** about $45–90/mo; GMV = units × average
  price, "directional" ([3P, Oct 2026](https://www.hubfluence.io/blog/kalodata-vs-fastmoss)).

## Top 5 under ~100 EUR/month for "who started spending big recently, by category and country"

1. **Meta Ad Library EU reach, pulled by API** (free from Meta, or $3.40–5.80 per 1,000 ads on
   Apify): the only platform-reported exposure figure covering all commercial ads in the EU; sum
   reach per advertiser page per week. Reach, not spend; Meta only; no US commercial data.
2. **Trendtrack Pro** (~$62/mo annual): a ready-made version of #1 with an API; 10 brands at once;
   spend method unpublished.
3. **Semrush Advertising Base** (€94.94/mo annual): Google Search and Shopping, FR and US,
   Position Changes shows advertisers moving into keywords; no API on this tier.
4. **SpyFu** ($39; history from ~$79–119): the cheapest Google spend estimate with an API;
   single-account test ~40 % of actual.
5. **SerpApi Google Ads Transparency API** ($25–75/mo) or **Adyntel** ($44 for 5k credits): an
   API-first launch detector, counting new creatives per advertiser by `first_shown` in France;
   a proxy only.

Just over budget or out: AdClarity Basic ($129), PowerAdSpy top tiers, Similarweb Ads ($542/mo
annual), Adbeat (spend on Enterprise), Sensor Tower and MediaRadar (enterprise, ~$25k/yr median).
