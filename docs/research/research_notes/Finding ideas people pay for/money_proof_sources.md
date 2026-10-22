# Money-proof sources: public evidence that people already pay for a job (other than advertising), October 2026

Checked on 2026-10-22. Tags used below: **[live check]** = I called the API or loaded the page myself on 2026-10-22; **[snippet]** = seen only in search-result text, page not opened; **[vendor]** = the source sells a competing tool; **[seller claim]** = a figure from a for-sale listing. Money amounts are in the source's currency.

## 1. App marketplaces with demand or revenue proxies

### Takeaway
The marketplaces fall into three tiers. The **Atlassian Marketplace** is the richest free source: a public REST API returns installs, reviews and the full price ladder, and sorts apps by "top-grossing". **WordPress.org** (free API with active installs and daily downloads), **Chrome Web Store** (user counts on listings), **Google Workspace Marketplace** and **HubSpot** (install counts on listings) give usage, not revenue. **Shopify** shows only reviews and price plans, so install counts come from third-party storefront scanners (StoreCensus), and revenue estimates are models. Zapier, Salesforce AppExchange, Microsoft Marketplace, Notion and Figma give supply or ranking signals at best. Every revenue estimate is price × users × an assumed paid share, and the people who publish these estimates say they can be off by 10x.

### Cited Findings

#### Shopify App Store
- A listing page shows the rating, the exact review count, price plans, category, launch date, developer address, languages and "works with" integrations, but no install count. Example (Klaviyo): 4.7 stars, "Reviews (3,404)", plans "Free", "$15 / month" (SMS) and "$20 / month" (251–500 contacts), launched "September 20, 2012" [live check] — [Shopify App Store, Klaviyo listing](https://apps.shopify.com/klaviyo-email-marketing)
- RevenueHunt's "State of the Shopify app economy" (June 2026 snapshot) covers 22,546 live apps, using public listing fields only — [RevenueHunt, June 2026](https://revenuehunt.com/state-of-the-shopify-app-economy/)
- Reviews in that snapshot: 51% of apps have never been reviewed, 81% have fewer than 10, and the median among reviewed apps is 5 — [RevenueHunt](https://revenuehunt.com/state-of-the-shopify-app-economy/)
- Revenue in that snapshot is "modelled from each app's published pricing tiers together with review and install signals". It estimates that the top 1% (225 apps) take 72% of revenue and that about 36% of apps earn anything. The page warns: "Treat the revenue figures as a directional model… not as billing data." The publisher is itself a quiz app featured in the analysis — [RevenueHunt](https://revenuehunt.com/state-of-the-shopify-app-economy/)
- Pricing in that snapshot: the most common entry price is $9.99 (1,447 apps), and 6.7% of apps (1,502) carry Built for Shopify status. The page's "completely free" share is internally inconsistent (47% in one place, 21% in another) — [RevenueHunt](https://revenuehunt.com/state-of-the-shopify-app-economy/)
- An older practitioner method (about 2021) estimates an app's revenue from its price and review count through two conversion rates: reviews per install, then paying share. The author gives a loose "5 to 40" ratio with undefined units and declines to produce estimates — [Kunal M., Exploring the Shopify App Store](https://kunalm.substack.com/p/exploring-the-shopify-app-store)
- StoreCensus publishes free app pages with active installs detected by "storefront signature analysis". Example (Judge.me): 366,458 stores as of 21 Oct 2026, out of 2,135,941 tracked stores. The page shows net change (+20,688 over 30 days, +90.8% year on year) and top countries (US 105,347; France 18,086). Data updates weekly, and a request cap leads to "Subscription Required". The page has internal inconsistencies [live check] — [StoreCensus, Judge.me](https://www.storecensus.com/stats/app/judgeme)
- Third-party Shopify app trackers include AppJubilee (daily keyword positions across about 1,200 App Store terms; history and alerts gated), Ablestar AppNavigator, AppstorePulse, Letsmetrix and others [vendor; snippet] — [AppJubilee, 10 tools for competitor rank tracking](https://blog.appjubilee.io/shopify-competitor-rank-tracking-tools)
- Apify actors scrape the App Store (apps, categories, keyword ranks, reviews, pricing plans). One lists $2.00 per 1,000 app details [snippet] — [Apify, shopify-app-intel](https://apify.com/carmentara/shopify-app-intel); [Apify, Applora](https://apify.com/scoutlayer/applora)
- AppJubilee claims listings with fewer than 25 reviews convert about 1–2% of views to installs, against 5–8% for those with 200+. No data source is given [snippet] — [AppJubilee blog](https://blog.appjubilee.io/shopify-partners-review-data-ranking-impact/)

#### Chrome Web Store
- Listings now show a large user count: Grammarly's page reads "41,000,000 users", with "3.9 out of 5 stars". From an EU IP the page first redirects to a Google consent wall [live check] — [Chrome Web Store, Grammarly](https://chromewebstore.google.com/detail/kbfnbcaeplbcioakkpcpgfkobkghlhen)
- In 2020, counts were bucketed ("900k+", "1M+") and capped at "10M+". The 2026 listing above shows a figure beyond that cap, so the display has changed — [DebugBear, Counting Chrome extensions (2020, updated 31 Aug 2026)](https://www.debugbear.com/blog/counting-chrome-extensions)
- DebugBear's 2020 count: 137,345 extensions plus 39,263 themes. 70% of extensions had fewer than 100 users, 337 had more than 1M, and the median was 17 installs — [DebugBear](https://www.debugbear.com/blog/counting-chrome-extensions)
- DebugBear's revenue estimate multiplies price by installs, says it "may well be off by an order of magnitude", and gives one extension a range of "$8k and $502k a year" because of country pricing — [DebugBear](https://www.debugbear.com/blog/counting-chrome-extensions)
- The official Chrome Web Store API (V2; V1 was current until October 2025) only publishes and manages your own items. It is "primarily intended for personal use on the developer's own extension" and exposes no statistics for other developers' extensions — [Chrome for Developers, Chrome Web Store API](https://developer.chrome.com/docs/webstore/api)
- Chrome-Stats (from the same team as firefox-stats.com) has run a crawler since late 2020 that takes daily snapshots of public store data. It covers Edge and Firefox since 2022, offers historical graphs, CSV export, alerts and API access on premium, and has a free tier with ads [snippet] — [About Chrome-Stats](https://firefox-stats.com/about)
- Chrome-Stats pricing is unclear: Capterra lists $50 a month flat, AlternativeTo lists $5–44 a month, SaaSHub (2022 screenshot) lists $9.99–14.99. chrome-stats.com returned a Cloudflare challenge to my fetch [snippet] — [Capterra, ChromeStats](https://www.capterra.com/p/236782/ChromeStats/); [AlternativeTo](https://alternativeto.net/software/chromestats/about)
- Example money ratio: a Flippa listing is titled "Fully automated Chrome extension with 17.4k active users, 7.3k yearly profit" [seller claim; title only] — [Flippa listing 12839069](https://flippa.com/fr/12839069-fully-automated-chrome-extension-with-17-4k-active-users-7-3k-yearly-profit-zero-costs-set-and-forget-passive-income-asset)

#### WordPress.org plugin directory
- The plugin API needs no key. `query_plugins` returns `active_installs`, `downloaded`, `rating`, `num_ratings`, `support_threads`, `support_threads_resolved`, `last_updated`, `added`, `tags` and `requires_plugins`. A search for "invoice" returned 1,996 plugins. Example: WooCommerce PDF Invoices & Packing Slips shows active_installs 300000, 24,231,521 downloads, 1,865 ratings, updated 2026-10-20 [live check] — [WordPress.org plugin API, query "invoice"](https://api.wordpress.org/plugins/info/1.2/?action=query_plugins&request%5Bsearch%5D=invoice&request%5Bper_page%5D=3)
- A second free endpoint gives daily download history, e.g. 4,733 downloads on 2026-10-16 and 67,229 on 2026-10-20, an update day. Daily downloads therefore include update downloads [live check] — [WordPress.org downloads-history endpoint](https://api.wordpress.org/stats/plugin/1.0/downloads.php?slug=woocommerce-pdf-invoices-packing-slips&limit=7)
- A third endpoint gives the share of installs by plugin version (e.g. "5.16": 61.04%) [live check] — [WordPress.org version-share endpoint](https://api.wordpress.org/stats/plugin/1.0/?slug=woocommerce-pdf-invoices-packing-slips)
- Active installs are bands: "a plugin showing 10,000+ has somewhere between 10,000 and 19,999 active installs" — [Plugin Gap (free tool on the WordPress.org API)](https://arcade.pirillo.com/plugin-gap.html)
- Practitioner tools scan for gaps with installs, ratings, update recency and support resolution. Plugin Gap queries the API live. The wpgoldmine MCP server finds "established plugins weakened by abandonment, low ratings, or poor support" and scores opportunity, abandonment and monetization (undated) — [Plugin Gap](https://arcade.pirillo.com/plugin-gap.html); [wpgoldmine MCP](https://glama.ai/mcp/servers/Bishop81/wpgoldmine-mcp)
- Example money ratio: a five-plugin CRO portfolio launched in 2015, with "over 166,000 combined active installations", earns about $4.3K gross a month with a c. 37% renewal rate [seller claim] — [FE International listing](https://feinternational.com/buy-a-website/31827-saas-digital-product-wordpress-cro-marketing-plugin-43k-gross-mo)

#### Atlassian Marketplace
- The public REST API (`/rest/2/addons`) needs no key. Each app comes with `distribution.downloads`, `totalInstalls` and `totalUsers` (-1 when hidden), plus `reviews.averageStars` and `count`. Example: "Timesheet Tracking for Jira" shows 12,775 installs and 251 reviews; Tempo Timesheets shows 26,287 installs and 898 reviews. The search "timesheet" returned 186 apps [live check] — [Atlassian Marketplace API, search "timesheet"](https://marketplace.atlassian.com/rest/2/addons?text=timesheet&limit=2&withTotalCount=true)
- The API sorts by `top-grossing`, a revenue rank. 8,414 apps were returned; the top five were draw.io (60,741 installs), ScriptRunner for Jira, Xray, Tempo Timesheets and JMWE [live check] — [Atlassian Marketplace API, sort=top-grossing](https://marketplace.atlassian.com/rest/2/addons?sort=top-grossing&limit=5)
- The pricing endpoint returns the full public price ladder by user tier. Example: 85 tiers for the timesheet app; the cloud annual tier for 100 users is $850 (renewal $425), and per-user monthly rates run $0.85 (100 users) down to $0.45 (1,000 users) [live check] — [Atlassian pricing API](https://marketplace.atlassian.com/rest/2/addons/com.tda.timesheet.report/pricing/cloud/live)
- Atlassian claims "$6B+ in Marketplace lifetime sales", "6,000+ apps and integrations" and "more than 2,000 third-party vendors". The page gives no date and no revenue-share percentage — [Atlassian Developer, Marketplace](https://developer.atlassian.com/platform/marketplace/)
- Earlier milestones: $1B lifetime (post marking it: 1,000+ vendors; about three-quarters of the prior year's $300M app sales went to developers) and $4B in late January 2024 [snippet for $4B] — [Atlassian, $1B in lifetime sales](https://www.atlassian.com/blog/developer/a-milestone-moment-1b-in-lifetime-sales); [Atlassian, Marketplace momentum](https://www.atlassian.com/blog/innovation/marketplace-momentum)
- The July 2024 partner update reports roughly 20,000 app installs a week across 5,700+ apps [snippet] — [Atlassian, July 2024 partner program update](https://www.atlassian.com/blog/developer/july-2024-marketplace-partner-program-tier-membership-update)
- Practitioner stories:
  - A developer who began as a side project in 2014 runs ten apps with over $1.2M lifetime revenue. He went full-time at about $10,000 MRR [snippet; self-reported, 2016–2019] — [Atlassian blog, developer turned Marketplace entrepreneur](https://www.atlassian.com/blog/developer/developer-turned-atlassian-marketplace-app-entrepreneur); [AMA](https://community.atlassian.com/forums/App-Central-articles/LIVE-AMA-with-Vitalii-Zurian-on-his-Marketplace-app-success/ba-p/1150982)
  - "Agile Docs" reported $4,149 MRR 18 months after launch (Nov 2020) [snippet; self-reported] — [Indie Hackers, Reaching $4,149 MRR in the Atlassian Marketplace](https://www.indiehackers.com/post/reaching-4149-mrr-in-the-atlassian-marketplace-a3cc93a067)

#### HubSpot App Marketplace
- Cards show install counts, e.g. "531K installs", "500+ installs", "20+ installs", "<10 installs". The "Most popular" section runs in install order (531K down to 144K). The text capture showed no ratings, prices or category filter on cards, and no total app count [live check] — [HubSpot App Marketplace](https://ecosystem.hubspot.com/marketplace/apps)

#### Salesforce AppExchange
- Install and lead metrics are reports for the publisher, viewed after signing in to AppExchange Publishing (an old developer-guide page) [snippet] — [Salesforce developer docs, AppExchange analytics reports](https://developer.salesforce.com/docs/atlas.en-us.194.0.packagingGuide.meta/packagingGuide/appexchange_analytics_reports.htm)
- Third-party scrapers say they collect public ratings, reviews, pricing and editions [vendor; snippet] — [Apify, Salesforce AppExchange scraper](https://apify.com/automation-lab/salesforce-appexchange-scraper)
- A 2024 SFApps "State of AppExchange" analysis of rating and review distribution is gated behind an email form; the page returned 403 to me [snippet] — [MarketingProfs, State of Salesforce AppExchange](https://www.marketingprofs.com/chirp/2024/52043/state-of-salesforce-appexchange-app-marketplace-infographic)

#### Zapier app directory
- The directory shows "10342+ apps" and 15 categories with app counts: Sales & CRM 2,024; Marketing 1,223; Commerce 888; Communication 791; Artificial Intelligence 749; Productivity 661; IT Operations 595; Content & Files 489; Human Resources 308; and others. There are no per-app usage numbers and no partner-tier badges [live check] — [Zapier app directory](https://zapier.com/apps)

#### Google Workspace Marketplace
- Listings show an install count, rating, review count, a pricing label and the update date. Example (Yet Another Mail Merge): "16M+", 4.7 stars, 18,106 reviews, "Free of charge with paid features", "Listing updated: October 21, 2026" [live check] — [Google Workspace Marketplace, YAMM](https://workspace.google.com/marketplace/app/yet_another_mail_merge_mail_merge_for_gm/52669349336)

#### Microsoft AppSource (now Microsoft Marketplace)
- In September 2025 Microsoft merged AppSource and Azure Marketplace into "Microsoft Marketplace". Old AppSource URLs forward to marketplace.microsoft.com, and the site has 3,000+ AI apps and agents [snippet; trade press] — [RCP Magazine, Sep 2025](https://rcpmag.com/blogs/rcp-channel-briefing/2025/09/microsoft-unifies-marketplaces.aspx); [SD Times](https://sdtimes.com/msft/microsoft-unveils-reimagined-marketplace-for-cloud-solutions-ai-apps-and-more/)

#### Notion and Figma template marketplaces
- Notion: paid templates are open only to approved creators in eligible countries, and review "may take a few months". The fee is 8% + $0.40, plus 1% FX for non-US creators — [Notion Help, Selling on Marketplace](https://www.notion.com/help/selling-on-marketplace)
- Notion's public pages show the price or "Free", category totals (Finance: "3,716 Templates") and "Popular"/"Duplications" sorts, but no purchase or duplication counts. Views, duplications and revenue appear only in the creator dashboard — [Notion Finance templates](https://www.notion.com/templates/category/finance)
- Figma Community: "We are not approving new creators to sell paid files on Community at this time." The fee is a flat 15% and the minimum price $2 — [Figma Help, About selling Community resources](https://help.figma.com/hc/en-us/articles/12067637274519-About-selling-Community-resources)

### Inferences
- **Catalog (state on 2026-10-22):**

| Source | Evidence of payment | Access | Cost | Terms / limits | Extract |
|---|---|---|---|---|---|
| Atlassian Marketplace | Installs + public price ladder + top-grossing rank | Public REST API, no key | Free | Terms not read | installs, users, reviews, price per tier, top-grossing rank, category, hosting |
| WordPress.org | Active installs (banded), downloads, ratings; no prices | Public API, no key | Free | Terms not read | active_installs, num_ratings, support resolution, last_updated, tags, daily downloads |
| Chrome Web Store | User counts, ratings; no revenue | Listing pages (consent wall in EU); no stats API | Free; Chrome-Stats ~$5–50/mo | Google terms not read | users, ratings, category, update date, paid/freemium wording |
| Shopify App Store | Review counts + price plans; installs only via scanners | Manual, scraping (Apify), StoreCensus, AppJubilee | Free to ~$2 per 1,000 apps | Shopify terms not read | reviews, plans, launch date, category, BFS badge, StoreCensus installs and growth |
| Google Workspace Marketplace | Install count, reviews, pricing label | Listing pages | Free | Not read | installs, reviews, "paid features" label |
| HubSpot | Install counts | Listing pages | Free | Not read | installs, "Most popular" order |
| AppExchange | Ratings, reviews | Pages, scrapers | Free | Not read | review counts, pricing |
| Zapier | Supply only (apps per category) | Directory | Free | Not read | category counts |
| Notion / Figma | Ranking and price only | Pages | Free | Figma closed to new sellers | price, category size, popularity order |

- **Revenue rule of thumb** (bets, each from a single data point; check against more):
  - **Atlassian.** Revenue ≈ installs × the price at the typical tier × paid share. Its top-grossing sort plus prices lets you rank a category without guessing conversion.
  - **WordPress.** One seller-claimed portfolio earns about $0.026 gross per active install per month ($4.3K ÷ 166K).
  - **Chrome.** One seller-claimed extension earns about $0.42 profit per user per year ($7.3K ÷ 17.4K).
  - **Shopify.** Revenue ≈ (StoreCensus installs or a reviews-based estimate) × price × paid share. The RevenueHunt snapshot says the distribution is extremely skewed, so the median app earns little.
- **The 10,000 EUR/month profit bar.** Roughly 12,000–13,000 EUR a month of revenue after platform share and costs (a bet: high software margin). That works out to:
  - Shopify: about 600–650 merchants paying $20 a month.
  - Atlassian: about 175 customers paying the $850/year 100-user cloud tier.
  - WordPress: at the portfolio ratio above, roughly 480K active installs, which is why commercial WordPress niches need a high price per site.
- **What to extract to spot a niche.**
  - A category where several apps sit in the 5K–50K install range with paid plans, ratings below 4.3 or poor support resolution, no update in 12+ months, and reviews that complain about a missing job.
  - On Atlassian, a category where mid-ranked top-grossing apps have modest installs (high price per install).
- **Watch for.** Bands hide 2x differences (WordPress, HubSpot). Downloads include updates. User counts can be gamed. Free installs dominate. Revenue estimates are models.

### Gaps
- Shopify's App Store terms on scraping, and its revenue-share terms as of October 2026: not verified.
- Store Leads pricing: page 404.
- Whether Salesforce AppExchange or Microsoft Marketplace show install counts publicly in 2026: not verified.
- HubSpot listing pages (pricing, reviews): not opened.
- Atlassian's revenue share for cloud and Forge apps: not stated on the page.
- The Chrome Web Store's terms on automated access: not read.
- What Atlassian's "top-grossing" sort is computed from (window, gross vs net): undocumented, as far as I found.
- No independent, dated benchmark of reviews-per-install or paid conversion for Shopify, Chrome or WordPress apps. The figures above are single seller claims or vendor models.

## 2. Revenue-transparent directories (TrustMRR, Indie Hackers, Open Startups, Baremetrics)

### Takeaway
TrustMRR is the one large, current directory where revenue is pulled from the payment processor: "over 15,000 startups listed" and "over 3,000 for sale", in 20 categories, with an authenticated API that filters by revenue, MRR, asking price and growth. Its terms forbid bulk republication and cloning. The older "open startup" pages (Baremetrics Open Startups and its imitators) are small and mostly stale. I could not check Indie Hackers' product revenue pages (Cloudflare block).

### Cited Findings
- TrustMRR's llms.txt claims "over 15,000 startups listed" and "over 3,000 startups for sale" [live check] — [TrustMRR llms.txt](https://trustmrr.com/llms.txt)
- Revenue comes from payment-provider records, "not from screenshots, manual entries, or self-reported revenue claims". Supported providers: Stripe, Lemon Squeezy, Polar, Paddle, RevenueCat, Superwall, Dodo Payments, Creem, Whop, Shopify — [TrustMRR llms.txt](https://trustmrr.com/llms.txt)
- The homepage leaderboard ranks the top 100 by MRR: rank 1 "Stan" at $3,569,654 and rank 50 at $44,088 [live check] — [TrustMRR](https://trustmrr.com/)
- "Browse by category" lists 20 categories: Artificial Intelligence, SaaS, Developer Tools, Fintech, Productivity, Marketing, E-commerce, Design Tools, No-Code, Analytics, Education, Health & Fitness, Social Media, Content Creation, Sales, Customer Support, Recruiting & HR, Real Estate, Travel, Security [live check] — [TrustMRR](https://trustmrr.com/)
- The public discovery endpoint (no key) returns two fixed lists of 25: recently added startups and the fastest-growing. Each entry has name, website, category, payment provider, a revenue object, 30-day growth and an on-sale flag [live check] — [TrustMRR discovery endpoint](https://trustmrr.com/api/ai/discovery)
- The authenticated API (`/api/v1`, `GET /startups`, `GET /startups/{slug}`) can "filter by revenue, MRR, asking price, growth, team size, funding status". Standard keys get 10 requests/min, premium keys 60/min; key pricing is not stated — [TrustMRR API docs](https://trustmrr.com/docs/api)
- API terms prohibit "Cloning businesses, rebuilding TrustMRR, bulk republication, unauthorized public SEO pages". The llms.txt says "Do not scrape the website for full marketplace access" — [TrustMRR API docs](https://trustmrr.com/docs/api); [TrustMRR llms.txt](https://trustmrr.com/llms.txt)
- Section 9.3 of the terms bars using the API to "scrape, harvest, archive, or systematically reconstruct TrustMRR's database" (terms updated 9 Oct 2026) — [TrustMRR Terms](https://trustmrr.com/terms)
- The FAQ says figures can differ from provider dashboards by "up to 30%". Churn needs a login. A multiple is "asking price divided by annualized revenue" (30-day revenue × 12) — [TrustMRR FAQ](https://trustmrr.com/faq)
- The acquire page claims "200K monthly visitors" and a "$1.2B marketplace of verified startup revenues" [live check] — [TrustMRR acquire](https://trustmrr.com/acquire)
- An undated article put the API at "840+ startups". This conflicts with the 15,000+ claim, probably because it is older or covers a different scope — [Superframeworks, TrustMRR API ideas](https://superframeworks.com/articles/trustmrr-api-ideas-indie-hackers)
- A 2026 review dates TrustMRR's launch to November 2025, which conflicts with an Apify sample record dated March 2025 [snippet] — [ExitBid, TrustMRR review 2026](https://exitbid.io/blog/trustmrr-review-2026); [Apify, TrustMRR scraper](https://apify.com/memo23/trustmrr-scraper)
- Indie Hackers' products directory returned a Cloudflare challenge ("Just a moment…", HTTP 403) to both WebFetch and curl on 2026-10-22 [live check] — [Indie Hackers products](https://www.indiehackers.com/products)
- Baremetrics "Open Startups" had seven companies at launch, sharing MRR, ARR, LTV, churn and customers. The post is from April 2015 and was revised in December 2023 [snippet] — [Baremetrics, Open Startups](https://baremetrics.com/blog/open-startups)
- Baremetrics "Open Benchmarks" published anonymized medians from 600+ small and mid-size SaaS companies; the benchmarks URL I tried returned 404 [snippet] — [VentureBeat, Baremetrics Open Benchmarks](https://venturebeat.com/business/baremetrics-open-benchmarks); [Baremetrics Open](https://baremetrics.com/open)
- Smaller verified-revenue boards, all unconfirmed as live in October 2026 [snippet]:
  - Dodo Payments "Build Publicly" (syncs twice a day) — [Build Publicly](https://index.dodopayments.com/build-publicly)
  - StartuPage revenue leaderboard (beta, Stripe-linked) — [StartuPage](https://startupage.featurebase.app/p/new-public-revenue-leaderboard-is-live)
  - MakerLead (top 100 Stripe-verified) — [BetaList, MakerLead](https://betalist.com/startups/makerlead)
  - Open Startup List (full disclosure required) — [t3n](https://t3n.de/news/?p=1265810)

### Inferences
- **Catalog:**

| Source | Evidence | Access (Oct 2026) | Cost | Limits |
|---|---|---|---|---|
| TrustMRR | Processor-verified revenue, MRR, growth, category | Public pages and discovery endpoint; filtered API with key | Free browsing; key pricing unknown | No scraping, no bulk republication, no clones |
| Indie Hackers | Self- or Stripe-reported revenue | Website (blocks bots) | Free | Not verified |
| Baremetrics Open and copies | A few live dashboards | Website | Free | Small, stale |

- **To find categories where small teams make 5–20k/month:**
  - Use the TrustMRR API (internal analysis only) to pull startups per category with MRR between 5k and 20k, at least 12 months old, with positive 30-day growth.
  - Count them per category and record MRR per customer (ARPU), payment provider (B2B on Stripe vs consumer on RevenueCat or App Store), on-sale status and asking multiple.
  - A category with many 5–20k startups and few above 100k is a good sign that a solo founder can reach the bar there without venture funding.
- **Sample bias.** TrustMRR over-represents indie, AI and builder-audience products (Marc Lou's audience). Categories like vertical SMB software for trades will be under-represented, so absence there is not evidence of no market.
- **The top-100 leaderboard is useless for the 5–20k band**, because rank 50 is already $44k MRR. Use category pages or the API.

### Gaps
- TrustMRR category pages (/category/{slug}) and the list-startups API parameters: not fetched.
- TrustMRR API key pricing.
- Whether Indie Hackers still shows revenue on product pages in 2026: blocked.
- The current state of Baremetrics Open Benchmarks: 404.
- No dated practitioner write-up that used TrustMRR category data to choose a niche (only the undated Superframeworks ideas list).

## 3. Acquisition marketplaces and 2025–2026 multiples

### Takeaway
Three marketplaces show per-listing money data with no account: Flippa (asking price, monthly revenue and profit, multiple, age), Empire Flippers (net profit, revenue, niche, monetization, 6–12-month trend) and TrustMRR (verified revenue and asking price). Acquire.com, Microns and the brokers put financials behind paid plans or NDAs. The terms of Flippa, Acquire.com and TrustMRR forbid scraping or rebuilding their data.

Small online businesses sold in 2025 to H1 2026 for about 1.4–3.9x annual profit:

| Source | Multiple of annual profit |
|---|---|
| Acquire.com, SaaS median | 3.9x |
| Flippa H1 2026, SaaS average | 2.47x |
| Empire Flippers, typical deal | 2.2–2.3x |
| Flippa, content | 2.3–2.6x |
| Flippa, e-commerce | 1.4–1.6x |

(Research for this section was run by a sub-agent on 2026-10-22; I spot-checked the Acquire.com report.)

### Cited Findings

#### Flippa
- Logged out, the SaaS search shows per card: asking price, monthly revenue, monthly profit, profit multiple, age, industry, country, a "Data Verified" badge and seller type. It read "Showing 1-50 of 679", with sort by "Most Profitable" and a "Monthly Profit" filter — [Flippa search, SaaS](https://flippa.com/search?filter%5Bproperty_type%5D%5B%5D=saas)
- Example cards — [Flippa search, SaaS](https://flippa.com/search?filter%5Bproperty_type%5D%5B%5D=saas):
  - "AI Captioning SaaS - $5.5K MRR, 3 years old" (France): revenue $5.83K/mo, profit $3K/mo, 3.1x, asking $110,000.
  - "Svgator": revenue $47.9K/mo, profit $28.1K/mo, 3.3x, asking $1,100,000.
- Titles and fields can disagree, and type tags can mislead (an affiliate casino site tagged SaaS) — [Flippa search](https://flippa.com/search?filter%5Bproperty_type%5D%5B%5D=saas)
- Premium costs USD 49/month or 388/year. It shows listings over $10K "21 days before the rest" and auto-accepts NDAs (free users wait "on average four days") — [Flippa Premium](https://flippa.com/product/premium)
- Terms, section 3: "you may not utilize any data mining, robots, or similar data gathering and extraction tools…" and "may not… create and/or publish your own database that features substantial parts of the Flippa Services". The revision date on the page equals the check date, so it may be auto-generated — [Flippa Terms of Service](https://flippa.com/terms-of-service)
- H1 2026 report (updated 2026-07-24): 123,022 active buyers. Profit multiples by model, average / top quartile — [Flippa H1 2026 Insights](https://flippa.com/blog/the-new-era-of-digital-ma-flippas-h1-2026-insights-report/):

| Model | Average | Top quartile |
|---|---|---|
| SaaS | 2.47x | 4.06x |
| Content | 2.32x | 4.68x |
| App | 2.62x | 5.46x |
| E-commerce | 1.55x | 2.75x |
| Service | 1.43x | 2.31x |
| Marketplace | 3.33x | not given |

  No period or sample size is given.
- H1 2026 by deal size: $10K–$100K 2.24x / 5.96x; $100K–$250K 1.85x / 3.82x; $250K–$1M 1.82x / 2.84x; $1M+ 2.50x / 5.42x — [Flippa H1 2026](https://flippa.com/blog/the-new-era-of-digital-ma-flippas-h1-2026-insights-report/)
- Flippa 2025 (Jan–Dec 2025): SaaS 2.7x / 5.8x; Content 2.6x / 5.5x; Apps 2.4x / 5.4x; E-commerce 1.4x / 2.7x; Services 1.2x / 2.1x. The text also says "up to 5.8x revenue for SaaS", which contradicts its own profit-based table — [Flippa 2025 M&A Insights](https://flippa.com/blog/2025-online-business-ma-insights-from-flippa/)
- H1 2026: SaaS sold deals rose 21% and content fell 39%, half on half. Buyers' top search terms were Shopify (13,009), YouTube (11,586), AdSense (6,228) and SaaS (6,191) — [Flippa H1 2026](https://flippa.com/blog/the-new-era-of-digital-ma-flippas-h1-2026-insights-report/)

#### Empire Flippers
- Logged-out cards show niche, monetization, asking price, net profit, revenue, multiple, "First Made Money" year and the 6–12-month change in profit and revenue. Example #97290: asking $1,008,564, net profit $272,586, revenue $348,982, 3.7x — [Empire Flippers marketplace](https://empireflippers.com/marketplace/)
- Since 8 Sept 2026, multiples are annual: listing price ÷ annual net profit. "About half of the listings… are priced below $300K." The 2026 industry report, converted to annual: Typical 2.3x, Premium 2.6x, seven-figure premium 3.4x, Distressed 1.1x — [Empire Flippers, Switching to annual multiples](https://empireflippers.com/switching-to-annual-multiples/)
- The live scoreboard (trailing 12 months) shows Typical 2.2x, Premium 2.4x, $1M+ Premium 3.2x and Distressed 1.1x. It also shows 2,681 listings sold, a sale price of 86% of list on average, 130 days to sell on average and 169 current listings — [Empire Flippers Scoreboard](https://empireflippers.com/scoreboard/)

#### Acquire.com
- The public SaaS page shows no listings ("Join for full access"). Buyer membership starts at $390 (period not stated) and unlocks "company names, financials, and direct messaging" — [Acquire.com SaaS for sale](https://acquire.com/saas-companies-for-sale/); [Acquire.com pricing](https://acquire.com/pricing/)
- Terms (4 Jan 2023) ban robots and spiders, "monitoring or copying", and republishing. The information is "for our users' internal business purposes only" — [Acquire.com Terms](https://acquire.com/terms/)
- Biannual Multiples Report "Jan 2026" (published 11 Feb 2026, updated 1 Sept 2026) — [Acquire.com Biannual Multiples Report, Jan 2026](https://blog.acquire.com/acquire-com-biannual-acquisition-multiples-report-jan-2026/):
  - "In both 2024 and 2025, SaaS businesses sold at a median profit multiple of 3.9x"; the average was in the "low-to-mid 4x range".
  - Average time on market was 81 days.
  - Average profit margin was 67% (2023) and 71% (2024).
  - Data is "anonymized, customer-provided", mostly under $10M enterprise value. No sample size is given. [I re-checked this page.]
- The Jan 2024 report, via a secondary source: 2023 average 4.3x profit; 4.11x under $100K, 4.97x for $100K–1M, 5.65x for $1M+ — [Investors Club, 17 Acquire.com statistics](https://investors.club/?p=23829)

#### Microns.io, Investors Club, Motion Invest, SideProjectors, Tiny Acquisitions
- Microns' public cards show category, "Annual Revenue" and "Asking Price" (and "Exit Price" when sold), but no profit or churn. Premium is $40/month or $299/year, and free users get deal flow "with 5 days delay" — [Microns.io](https://www.microns.io/); [Microns Premium](https://www.microns.io/premium)
- Investors Club: Premium $59/month or $390/year, with listings five days early and P&L and traffic. Motion Invest: content sites only, the price drops every two days. Both facts come from Investors Club's own comparison (29 Apr 2026) — [Investors Club vs Motion Invest](https://investors.club/investors-club-vs-motion-invest/)
- SideProjectors listings carry almost no revenue data, and many are pre-revenue — [SideProjectors](https://www.sideprojectors.com/)
- tinyacquisitions.com did not resolve (DNS) on 2026-10-22 — [attempted fetch](https://tinyacquisitions.com/)
- FE International's buy page shows no listing data and routes buyers to a contact form — [FE International, buy a website](https://feinternational.com/buy-a-website/)

#### TrustMRR (for sale)
- For-sale cards show category, monthly revenue, asking price and multiple. Examples: an Education app with $4.3k revenue asking $150k (2.9x); an AI app with $13k asking $1.5M (9.7x). Fees: a 3% marketplace fee plus Escrow.com fees; buyer alerts cost $199/year — [TrustMRR](https://trustmrr.com/); [TrustMRR FAQ](https://trustmrr.com/faq)

### Inferences
- **Price of the target.** 10,000 EUR/month profit (120K a year) trades at roughly 2.2–3.9x, i.e. about 265K–470K. Acquirers pay that because the cash flow is proven.
- **Listings as market evidence.** A category with several listings showing 5–20k/month profit, at least two years old, with a flat or rising trend, is a proven niche.
- **Fields to record per listing:**
  - ID, URL, date seen, status (ask, pending or sold)
  - The niche in one line ("who pays for what")
  - Model (subscription, one-time, ads, affiliate)
  - Monthly revenue and profit, and margin
  - Customers and ARPU
  - Churn (TrustMRR with login, Acquire.com paid)
  - 6–12-month trend, and age or first-revenue year
  - Main channel, owner hours, reason for sale
  - Verification (Flippa badge, TrustMRR processor link, EF vetting)
- **Weighting.** Sold prices beat asks (EF sells at 86% of list), and verified revenue beats claims. Listings over-represent declining businesses and owners who want out.
- **Compliant method.** Read a bounded sample of public cards by hand and keep cited notes. Full dumps break Flippa's, Acquire.com's and TrustMRR's terms.
- **Conflicts.** The 3.9x SaaS median (Acquire.com, SaaS-only, larger deals, undefined "profit") vs 2.47–2.7x averages (Flippa, many sub-$100K deals). Flippa's small-deal band jumped from 1.8x (2025) to 2.24x (H1 2026). Treat both as noisy.

### Gaps
- No marketplace publishes how many deals sit behind its multiples.
- Empire Flippers' unlock rules (proof of funds, 1:1 vs 1.5x): page returned 403.
- Quiet Light multiples: page returned 403.
- No French marketplace for websites or SaaS with public financials was found; CessionPME is general SME transfer.
- Acquire.com seller fees: conflicting.
- Newsletter-business multiples: not published by any marketplace checked.
- No dated practitioner write-up analysing listings by niche was found.

## 4. Labor budgets: job postings and freelance marketplaces

### Takeaway
Free, structured labor data exists for trends and for sizing a whole occupation, but access to individual postings has narrowed in 2026:
- **Trends and sizing:** Indeed Hiring Lab (CC BY 4.0, covers France), BLS OEWS and O*NET in the US, Eurostat online-ad statistics.
- **Closed or restricted:** France Travail's "Offres d'emploi" API is no longer exposed on francetravail.io (restricted on data.gouv.fr, modified 2026-10-20). Indeed's Publisher API is closed. LinkedIn bans scraping, and Welcome to the Jungle and APEC offer no public job API.
- **Freelance:** Freelancer.com has an open API with per-project budgets and bid statistics. Codeur.com shows French project budget brackets and offer counts. Upwork's RSS feeds have been gone since August 2024.

(Research for this section was run by a sub-agent on 2026-10-22; I re-checked France Travail and Freelancer.com live.)

### Cited Findings

#### Job postings
- France Travail's API: "L'API Offre d'emploi de France Travail n'est actuellement plus exposée sur www.francetravail.io le temps d'une analyse des modalités de distribution et de réutilisation du service", following "usages automatisés massifs". Access type "restricted", record modified 2026-10-20 [live check] — [data.gouv.fr, API Offres d'emploi](https://www.data.gouv.fr/dataservices/api-offres-demploi)
- Under the same record, local authorities, administrations, companies and associations may apply "under conditions"; private individuals may not. Rate limit "10 appels / seconde" — [data.gouv.fr dataservices API](https://www.data.gouv.fr/api/1/dataservices/?q=offres)
- France Travail lists 13 APIs on data.gouv.fr, among them "Marché du travail" (tension and trends by area), "ROME 4.0" and "Informations sur l'emploi dans un territoire". Four are restricted — [France Travail dataservices](https://www.data.gouv.fr/organizations/france-travail/dataservices)
- "Offres d'emploi diffusées à France Travail" is a quarterly raw-data xls under the Licence Ouverte, updated 2026-07-03. It includes offers republished from partner sites — [data.gouv.fr dataset](https://www.data.gouv.fr/datasets/offres-demploi-diffusees-a-france-travail)
- BMO 2026 survey (April 2026): about 2.3 million planned hires in France (−6.5%), 43.8% expected to be hard to fill [snippet] — [La finance pour tous, 24 Apr 2026](https://www.lafinancepourtous.com/2026/04/24/quels-besoins-en-main-d-oeuvre-en-france-en-2026/)
- APEC: no official API found. Its 2025 study gives a median cadre pay of €55,000 a year (26,000 cadres; 111 job families) [snippet] — [APEC, 111 familles de métiers 2025 (PDF)](https://corporate.apec.fr/files/live/sites/corporate/files/Nos%20etudes/PDF/Les%20remunerations%20des%20cadres%20dans%20111%20familles%20de%20metiers%202025.pdf)
- Welcome to the Jungle's robots.txt disallows `/*?` and `*/jobs?query=*` for all agents and publishes a sitemap index; no API documentation found — [welcometothejungle.com/robots.txt](https://www.welcometothejungle.com/robots.txt)
- Indeed Hiring Lab publishes daily job-postings indexes (refreshed weekly, 1 Feb 2020 = 100) for AU, CA, DE, ES, FR, GB, IE, IT, NL, US and the euro area. There are occupational-sector series and a French regional file, under CC BY 4.0 — [hiring-lab/job_postings_tracker](https://github.com/hiring-lab/job_postings_tracker)
- Indeed's Publisher API is closed to new integrations [vendor] — [JobsPipe](https://jobspipe.dev/blog/indeed-publisher-api)
- LinkedIn's job APIs are partner-only, for ATS and posting [snippet] — [Microsoft Learn, job posting](https://learn.microsoft.com/fr-fr/linkedin/talent/premium-job-posting/get-started-with-job-posting?view=li-lts-2025-01)
- In hiQ v. LinkedIn (Nov 2022) the anti-scraping terms were found enforceable. The case ended in a $500,000 consent judgment and a permanent injunction — [Proskauer, Nov 2022](https://newmedialaw.proskauer.com/2022/11/11/court-finds-hiq-breached-linkedins-terms-prohibiting-scraping-but-in-mixed-ruling-declines-to-grant-summary-judgment-to-either-party-as-to-certain-key-issues/); [Proskauer, settlement](https://www.proskauer.com/blog/hiq-and-linkedin-reach-proposed-settlement-in-landmark-scraping-case)
- US BLS OEWS (May 2025 data, scheduled for 15 May 2026) covers about 830 occupations [snippet] — [BLS OEWS technical notes](https://www.bls.gov/oes/2025/may/oes_tec.htm)
- O*NET publishes task statements per occupation (18,796 occupation–task links in 30.3). Web Services need registration and are CC BY 4.0 — [O*NET Web Services](https://services.onetcenter.org/); [O*NET What's New](https://onetcenter.org/whatsnew.html)
- Eurostat's experimental online-job-advertisement rate is published by 3-digit ISCO occupation. Known biases: IT over-represented, duplicates [snippet] — [Eurostat OJA rate](https://ec.europa.eu/eurostat/web/experimental-statistics/online-job-advertisement-rate)

#### Freelance marketplaces
- Upwork's RSS feeds ended after 20 Aug 2024; Upwork points users to saved searches with email alerts [snippet; 403] — [Upwork Help, RSS deprecation](https://support.upwork.com/hc/en-us/articles/52052528243731-RSS-deprecation)
- The old Upwork feed URLs return 404 as of May 2026 [vendor] — [Snipework](https://snipework.com/blog/upwork-rss-feed-2026)
- Upwork's API is GraphQL with OAuth 2.0, and key requests are reviewed by people [vendor] — [GigRadar help](https://help.gigradar.io/en/articles/12526340-what-is-an-upwork-api-key); [Upwork developer](https://www.upwork.com/developer)
- A client library documents a `marketplaceJobPostingsSearch` query [third party] — [NuGet Upwork](https://www.nuget.org/packages/Upwork/)
- A vendor reads Upwork's "API & MCP Terms" as forbidding using the API to "enumerate or continuously monitor" its content, and reports an official MCP server launched in August 2026 [vendor; unverified] — [UpHunt](https://uphunt.io/blog/upwork-job-scraper-2026)
- Freelancer.com: an unauthenticated call returns active projects with `budget.minimum/maximum`, currency, `bid_stats.bid_count` and `bid_avg`, and `time_submitted`. "bookkeeping" returned 26 active projects. Example: "Ongoing QuickBooks Bookkeeping", USD 5,000–10,000, 17 bids averaging 6,255.88 [live check] — [Freelancer.com API, active projects "bookkeeping"](https://www.freelancer.com/api/projects/0.1/projects/active/?query=bookkeeping&limit=2)
- Freelancer.com's keyword matching is loose: the top "data entry" hits were unrelated jobs — [Freelancer.com API, "data entry"](https://www.freelancer.com/api/projects/0.1/projects/active/?query=data%20entry&limit=3)
- Codeur.com project cards show title, date, status, a budget bracket ("Moins de 500 €", "500 € à 1 000 €", "1 000 € à 10 000 €", day-rate brackets), offer count, view count and skills. The site claims "Plus de 2 000 projets/mois"; no RSS or API seen — [Codeur.com projects](https://www.codeur.com/projects)
- ComeUp service pages show sales on the listing, the seller's total sales, rating and review count [snippet] — [ComeUp service page](https://comeup.com/fr/service/201741/creer-vos-comptes-et-microservices-optimises-et-personnalises-sur-comeup)
- Malt's latest "Freelancing in Europe" edition found is 2024 (5,000+ freelancers) [snippet] — [Malt, Freelancing in Europe 2024](https://www.malt.uk/resources/guide/freelancing-in-europe-2024)
- Malt UK rates page: strategy and business consultants £698/day, graphic designers £381/day [snippet; 403] — [Malt UK average rates](https://www.malt.uk/t/average-freelance-rates)
- Malt barometer (July 2026), French developer day rates: about €317 (0–2 years) to €672 (15+ years) [secondary] — [La Fabrique du Net](https://www.lafabriquedunet.fr/tarifs-des-developpeurs-freelances-dans-les-grandes-villes-de-france/)
- Fiverr's Business Trends Index (9 Jun 2026) measures searches, not orders (e.g. "Claude Code" skill searches +938%) — [Fiverr release PDF](https://fiverrinternationalltd.gcs-web.com/node/10161/pdf)
- Fiverr says its client activity insights come from public reviews and may not include all orders — [Fiverr Help, Client activity insights](https://help.fiverr.com/hc/en-us/articles/5247501745169-Client-activity-insights)
- The Oxford Online Labour Index method: poll platforms at intervals, count each new project as a vacancy, classify by occupation and employer country. It misses projects that open and close between polls — [OII, How the OLI is constructed](https://ilabour.oii.ox.ac.uk/how-the-online-labour-index-is-constructed/)
- Vendor rule of thumb (undated): look for tasks that recur weekly or monthly with job values of $500+, then check G2 and Capterra for software gaps [vendor] — [BigIdeasDB, Upwork analysis](https://bigideasdb.com/help/how-to-use-upwork-analysis)

### Inferences
- **Catalog:**

| Source | Evidence of payment | Access (Oct 2026) | Cost | Terms |
|---|---|---|---|---|
| France Travail offers API | Posted jobs (ROME, contract, salary) | Restricted; apply as a company | Not stated | Licence under review |
| France Travail open files and Marché du travail | Aggregates by occupation | Download or API | Free | Licence Ouverte (file) |
| Indeed Hiring Lab | Postings index (trend only) | GitHub CSV | Free | CC BY 4.0 |
| APEC, WTTJ, LinkedIn | Postings, salaries | Manual counts | Free | LinkedIn bans scraping; WTTJ blocks query URLs |
| BLS OEWS + O*NET | Employment × wage, task lists | Download, API | Free | CC BY (O*NET) |
| Freelancer.com | Budgets, bids, dates | Open API | Free | API terms not read |
| Codeur.com | Budget brackets, offers, views | Manual | Free | Not read |
| Upwork | Budgets, rates | Manual or approved API | Free | No continuous monitoring (vendor reading) |
| Fiverr, ComeUp | Gig prices, reviews or sales | Manual | Free | Fiverr terms not read |
| Malt | Day rates | Profiles, reports | Free | Not read |

- **Method to price one recurring task:**
  1. Write one sentence for the task, plus 5–10 French and English phrases (e.g. "rapprochement bancaire", "saisie comptable", "bank reconciliation").
  2. Map it to O*NET task statements (US), ROME codes (France) and ISCO codes (Eurostat).
  3. Sample for 4 weeks at a fixed cadence. Freelancer.com by API, grouped by `time_submitted`. Codeur brackets by hand. Upwork saved searches by hand. France Travail, Indeed.fr, WTTJ and APEC result counts by hand. Fiverr and ComeUp: starting price and review or sales count for the top 20–50 gigs.
  4. Label 50 hits per query as relevant or not, and apply that precision to the counts.
  5. Annualize three ways:
     - Freelance flow = new projects per month × precision × median budget × 12.
     - Hiring flow = deduplicated postings × median salary.
     - US employee stock = OEWS employment × wage × the task's share of time. The time share is a bet, to be measured in buyer interviews.
- **Pitfalls:** cross-posting duplicates, reposts, agencies posting for many buyers, loose keyword matching, currency and unit mixes, brackets read as prices, `bid_avg` being what sellers ask, fake postings, reviews undercounting orders.
- **For the 10K EUR/month test:** ongoing posts like "Ongoing QuickBooks Bookkeeping" (USD 5,000–10,000) show recurring budgets. About 25–40 such clients at a few hundred EUR a month would reach the bar as a productized service (a bet on retention and price).

### Gaps
- When France Travail's offers API stopped being exposed, whether it will return, and its full field list. The record also shows "availability 99.8", which contradicts "not exposed".
- Upwork's official GraphQL docs and API terms: both returned 403.
- Malt primary pages: 403; any edition after 2024.
- Fiverr's terms clause and any API.
- ComeUp totals; Codeur RSS or archives; Freelancer.com rate limits and API terms.
- WTTJ's terms; LinkedIn's current User Agreement text (2022 sources were used).
- Not researched: DARES and INSEE salary-by-occupation data, PeoplePerHour, Crème de la Crème, Collective, Toptal, Contra.
- No benchmark of how many orders get a review.
- No dated independent write-up measuring one task's volume and price across these platforms.

## 5. Search demand with commercial intent (Keyword Planner, CPC, Trends, Exploding Topics, Glimpse, SE Ranking)

### Takeaway
CPC is the cheapest public proxy of what a customer is worth to the advertisers already selling to them. Keyword Planner needs a Google Ads account with billing details, and low spenders reportedly get volume ranges. Programmatic Keyword Planner access now needs a Google Cloud project at Basic access with brand verification, because developer tokens were sunset on 9 Sept 2026. SE Ranking, which the founder has, returns volume, CPC, paid competition (0–1), difficulty (0–100), intent and 12 months of history per country database, through its UI and a credit-based API. Google Trends' official API is still an application-only alpha.

### Cited Findings
- Keyword Planner: "You must complete your account setup by entering your billing information" to use its features. The help page does not say actual spend is needed — [Google Ads Help, Use Keyword Planner](https://support.google.com/google-ads/answer/7337243?hl=en)
- Google confirmed in 2016 that accounts with low or no spend get search volumes as ranges (e.g. 1K–10K) [third party; still reported in 2026 guides] — [Search Engine Land, 2016](https://searchengineland.com/google-officially-throttling-keyword-planner-data-low-spending-adwords-accounts-255795)
- "Top of page bid (low range)" is the 20th percentile of top-of-page bids and the high range the 80th percentile, over the previous 30 days, for the chosen location and network — [Google Ads Help, About Keyword Planner forecasts](https://support.google.com/google-ads/answer/3022575)
- Google Ads API (page read 2026-10-22): "Developer tokens were sunset on September 9, 2026, and API access levels are now managed per Google Cloud project." Explorer access (2,880 production operations a day) cannot use the "Planning" services (KeywordPlanIdeaService). Basic (15,000 a day) requires brand verification; Standard requires a manual audit — [Google Ads API, access levels](https://developers.google.com/google-ads/api/docs/api-policy/access-levels)
- LocaliQ 2026 search-ad benchmarks (updated 1 Jun 2026, Google and Microsoft Ads campaigns), all-industry average CPC $5.42, CVR 8.18%, CPL $66.69 — [LocaliQ, Search advertising benchmarks](https://localiq.com/blog/search-advertising-benchmarks/):

| Industry | CPC | CPL |
|---|---|---|
| Attorneys & Legal Services | $9.87 | $131.63 |
| Home & Home Improvement | $8.33 | $90.92 |
| Dentists | $8.00 | not captured |
| Personal Services | $7.17 | not captured |
| Business Services | $5.87 | $93.69 (CVR 4.85%) |
| Industrial & Commercial | $5.87 | not captured |
| Career & Employment | $5.81 | not captured |
| Finance & Insurance | $3.39 | not captured |
| Real Estate | $3.22 | $102.51 |

- The 2025 edition reported $5.26 average CPC (16,446 campaigns, Apr 2024–Mar 2025), with CPC up in 87% of industries [snippet] — [Search Engine Land](https://searchengineland.com/google-ads-costs-rise-again-but-conversions-improve-report-455663); [PPC Land](https://ppc.land/google-ads-costs-rise-12-88/)
- "[Competitor] alternative", "X vs Y" and "best X software" queries are treated as bottom-of-funnel, high-converting terms. One 2023 post argues standalone comparison pages are now crowded by review aggregators and affiliates [agency blogs] — [Founderpath, compare pages](https://founderpath.com/blog/compare-pages-for-seo); [Healthy Competition, 2023](https://healthycompetition.beehiiv.com/p/build-competitive-comparison-landing-pages-2023)
- Google Trends API: "Get early access to the Google Trends API alpha"; applications only. It offers "a rolling window of the last 5 years", daily, weekly, monthly or yearly intervals, countries and sub-regions, and data "not scaled from 0 to 100". No quotas or pricing published — [Google, Trends API](https://developers.google.com/search/apis/trends)
- The alpha was announced in July 2025 — [Search Engine Journal](https://www.searchenginejournal.com/google-trends-api-alpha-launching-breaking-news/551935/)
- The unofficial pytrends library was reportedly shelved in April 2025 [snippet] — [DEV Community](https://dev.to/esteban_ortega/pytrends-is-dead-heres-how-to-get-google-trends-data-in-2026-1a18)
- Exploding Topics plans: Entrepreneur $39/month (100 tracked trends), Investor $99 (500, CSV export), Business $249 (2,000). All include "Trends Database", "Trending Products" and "Meta Trends", with a 7-day free trial and no free tier or API listed. The database has "1.1M+" entries [live check] — [Exploding Topics pricing](https://explodingtopics.com/pricing)
- Glimpse: a free tier capped at ten searches a month, paid from $99 a month (Glimpse's own guide) [snippet] — [Glimpse guide](https://meetglimpse.com/software-guides/trend-spotting-websites-tools/)
- Glimpse has no pricing page, as of August 2026 [snippet] — [Outlierkit](https://outlierkit.com/resources/glimpse-pricing/)
- SE Ranking API pricing: stand-alone pay-as-you-go from "€45.00" for "250K credits" ($50 minimum deposit), or bundled with plans (Core $129/mo, Growth $279/mo, API add-on from $149/mo). The page claims "188" country databases and "5.5B" keywords — [SE Ranking API](https://seranking.com/api.html)
- SE Ranking keyword endpoints return `volume`, `cpc`, `competition` (paid, 0–1), `difficulty` (0–100), `intents` (I/C/T/L/N) and `history_trend` (12 months), per required regional `source` database:

| Endpoint | Cost |
|---|---|
| Bulk `export` | "100 credits per request" for 1–5,000 keywords |
| `similar` / `related` / `questions` | 10 credits per returned keyword |
| `longtail` | 1 credit per returned keyword |

  — [SE Ranking API docs, keyword research](https://seranking.com/api/data/keyword-research/)
- SE Ranking's UI limits keyword history to six months on Core and any available month on Growth, and organic SERP history goes back to February 2020 [snippet] — [SE Ranking, historical data](https://seranking.com/blog/historical-data/)

### Inferences
- **CPC as a value floor.** A buyer paying $5.87 a click at a 4.85% conversion rate pays about $94 per lead (Business Services). Their customer is worth at least several times that, or they would stop bidding. A job whose "X software" keywords carry €5–15 CPCs is a job someone monetizes.
- **Keyword families to pull per job** (with SE Ranking in the FR and US databases):
  - "logiciel X", "X software", "X app"
  - "X alternative" and "alternative à X"
  - "X pricing" or "X prix"
  - "best X for [trade]"
  - "X template" or "modèle X" (people systematizing by hand)
  - "how to X" (informational, lower value)
- **Fields to extract per keyword:** volume, CPC, paid competition, difficulty, intent, 12-month trend.
- **Signals:** high CPC with high paid competition and only a few strong organic incumbents means a monetized job. "Alternative" searches on a named incumbent mean switching demand. Rising "template" searches mean manual workarounds.
- **Cost check.** Per SE Ranking's docs, a bulk export of up to 5,000 keywords costs 100 credits, so €45 of pay-as-you-go credits covers far more than one weekly idea needs. Verify actual consumption on one call before relying on this.
- **Keyword Planner as a second opinion.** It is free with a billing-enabled account; its top-of-page bid range (20th to 80th percentile) is a more defensible "what advertisers pay" figure than a tool's single CPC.
- **Trend tools.** Exploding Topics ($39/month) and Glimpse ($99/month) are for direction only. Neither proves payment, so spend only if a trend question blocks a verdict.

### Gaps
- Google's own current statement on ranged volumes for low-spend accounts: not found in the help pages read.
- Whether SE Ranking's API `source` list includes `fr`: the codes page was not read. The UI is known to cover France per its marketing, but this was not verified.
- How SE Ranking computes CPC and competition.
- No 2026 France-specific CPC benchmark by industry was found; LocaliQ is US-centred.
- Glimpse's official prices.

## 6. Technology adoption trackers (BuiltWith, Wappalyzer, SimilarTech, HTTP Archive, StoreCensus)

### Takeaway
Single-site lookups are free on BuiltWith and capped at 50 a month on Wappalyzer's free tier. Lists of sites by technology, with country filters and history, cost $250–495 a month, and both price that per month. BuiltWith's free Trends pages blocked automated fetches. The cheapest way to count sites per technology is HTTP Archive's public BigQuery tables, built from Wappalyzer detections on a crawl of tens of millions of pages. These have no country field and cost BigQuery query fees. For Shopify specifically, StoreCensus shows free per-app install counts, net change and top countries. SimilarTech's 2026 status and pricing could not be verified.

### Cited Findings
- BuiltWith: "BuiltWith is free to use for individual site lookups forever." Plans: Basic $295 (2 technologies), Pro $495 (unlimited), Team $995. All include "Trends and Technology History" (18+ years) and filtering "by spend, technology use, location and more". Reports need a paid plan, with a one-month minimum. The page claims 127,911 technologies tracked — [BuiltWith plans](https://builtwith.com/plans)
- BuiltWith's free Trends page (e.g. Shopify) returned a "BuiltWith verification" screen (HTTP 202) to both WebFetch and curl on 2026-10-22, so its counts could not be read [live check] — [BuiltWith Trends, Shopify](https://trends.builtwith.com/shop/Shopify)
- Wappalyzer:
  - Free tier: 50 lookups a month, 5 website alerts, sample lead lists.
  - Plans: Pro $250/month (one technology, 5,000 lookups), Business $450/month (any technologies, 20,000 lookups, 20,000 API credits), Enterprise $850+.
  - API calls cost about one credit per site, and plan credits expire after 60 days.
  — [Wappalyzer pricing](https://www.wappalyzer.com/pricing/)
- SimilarTech was freemium in 2016, with paid plans from $290 a month — [TechCrunch, 2016](https://techcrunch.com/2016/05/25/similartech-tells-you-whats-powering-any-website-alerts-web-companies-to-new-leads)
- A 2026 technographic-API roundup dropped SimilarTech because its www domain did not resolve, and found no Similarweb technographics pricing [snippet] — [Reply.io, technographic data APIs 2026](https://reply.io/blog/best-technographic-data-apis/)
- SimilarTech is now listed under Similarweb's sales-intelligence offering [snippet] — [Salesforge directory](https://salesforge.ai/directory/sales-tools/similartech)
- HTTP Archive `httparchive.crawl.pages`: one row per page tested monthly, with a `technologies` array "detected at runtime" (Wappalyzer), a CrUX `rank`, `client` (desktop or mobile) and `is_root_page`. No country field is listed. The example counts for May 2024 sum to about 54.7M pages, and an unsampled count query scans about 1 GB — [HTTP Archive docs, pages table](https://httparchive.org/docs/reference/tables/pages/)
- Forum guidance on counting sites per technology with these tables (e.g. a 2019 WordPress count of about 906,000 URLs) — [HTTP Archive forum, how many websites use a technology](https://discuss.httparchive.org/t/how-many-websites-use-a-particular-technology/1627)
- StoreCensus (Shopify apps) shows active installs, net 30-day, 90-day and year-on-year change, top countries and store industries. It updates weekly and puts heavier use behind a subscription (see section 1) [live check] — [StoreCensus, Judge.me](https://www.storecensus.com/stats/app/judgeme)

### Inferences
- **Catalog:**

| Tool | Countable for free | Paid tier | Limits |
|---|---|---|---|
| BuiltWith | Single-site lookups (Trends pages blocked bots) | $295–995/month; history, location filters, lists | One-month minimum |
| Wappalyzer | 50 lookups/month | $250–850+/month; lists, API credits | Credits expire after 60 days |
| HTTP Archive | Sites per technology per month (BigQuery) | BigQuery query cost | No country field; rank buckets via CrUX |
| StoreCensus | Per-app installs, growth, top countries | Subscription past a request cap | Detection can miss installs |
| SimilarTech | Unclear | Unclear | Unverified |

- **Use for money-proof.** A paid tool installed on many SMB sites, and growing, proves SMBs pay for that category. Examples: a booking widget on salon sites, an invoicing integration on WooCommerce, a review app on Shopify. Net adds over 30–90 days (StoreCensus), or month-over-month counts in HTTP Archive, show momentum.
- **What to extract:**
  - Count of sites per technology, and the change over 3, 6 and 12 months.
  - Share by country: FR vs US, from StoreCensus or BuiltWith paid.
  - Co-installed technologies (e.g. sites with tool X but without Y).
  - For a candidate niche, the incumbent's install base vs the size of the niche's site population.
- **Cheapest path.** HTTP Archive monthly technology counts (global), then StoreCensus for Shopify. One month of Wappalyzer Pro ($250) only if a lead list by technology is needed for outreach.

### Gaps
- What BuiltWith Trends' free pages show in 2026 (counts by country, sites added or dropped): blocked, unverified.
- Whether BuiltWith's paid plans show recently added or dropped sites: "Technology History" is listed, but no added/dropped report was confirmed.
- SimilarTech's 2026 pricing and free tier.
- BigQuery's free monthly query allowance: not verified this session; the pricing page did not render.
- Store Leads pricing: 404.
- The current Technology struct schema in HTTP Archive (version and categories): not read.

## 7. Company registries and public statistics (SIRENE, Pappers, BODACC, INSEE, Companies House, US Census)

### Takeaway
France's registries are open and free:
- **SIRENE:** a free API (30 requests/min) plus monthly full stock files in Parquet under the Licence Ouverte.
- **API Recherche d'entreprises:** no key, 7 requests/s. It filters by NAF code and by revenue (`ca_min`/`ca_max`) and net income, and returns each firm's creation date and published turnover.
- **BODACC:** an open API of 6.65 million creation notices with free-text activity descriptions.
- **INSEE statistics:** 2025 was a record (1,165,800 creations, +5%), led by administrative support (+11.7%, cleaning +18%), trade (+11.1%, specialised e-commerce +32%) and information-communication (+8.2%). Q3 2026 creations were up 16% year on year, with information-communication +55%.

NAF codes change on 1 Jan 2027 (NAF 2025), which will break time series. The UK (Companies House) and the US (Census Business Formation Statistics) offer equivalent free sources.

### Cited Findings
- **SIRENE stock files** (data.gouv.fr, monthly, Licence Ouverte v2): "Fichier StockUniteLegale - 01 octobre 2026" (Parquet, 713,585,991 bytes) and "StockEtablissement" (Parquet, 2,220,887,978 bytes) [live check] — [data.gouv.fr, Base Sirene](https://www.data.gouv.fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret)
- **API Sirene** on portail-api.insee.fr is free after registration. The quota is 30 queries a minute, with up to 1,000 results per call through cursors, and INSEE suggests the monthly stock files to avoid the cap [snippet of INSEE's June 2026 Sirene news; the page returned 404 to my fetch] — [INSEE, Sirene Open Data news](https://insee.fr/fr/information/3711739); [CompanyData, Sirene API](https://companydata.com/sirene-api/)
- **API Recherche d'entreprises**, no key:
  - "au maximum 7 requêtes par seconde par adresse IP", plus 30 per second per ASN.
  - Filters include `activite_principale`, `section_activite_principale`, `tranche_effectif_salarie`, `ca_min`, `ca_max`, `resultat_net_min`, `resultat_net_max`, `est_qualiopi`, `est_rge`, `est_organisme_formation`, `code_postal`, `departement` and `etat_administratif`.
  - Each result carries `date_creation`, `activite_principale_naf25` and `finances` (e.g. {"2024": {"ca": 558064199, "resultat_net": 9730844}}).
  - The search caps at 10,000 results.
  [live check] — [API Recherche d'entreprises, OpenAPI](https://recherche-entreprises.api.gouv.fr/openapi.json); [sample query, NAF 62.01Z](https://recherche-entreprises.api.gouv.fr/search?activite_principale=62.01Z&per_page=1&etat_administratif=A)
- **BODACC** open API (Opendatasoft): 6,653,295 notices with `familleavis` = "creation". Fields include `dateparution`, `departement_nom_officiel`, `registre` and `listeetablissements` with free-text activity. The latest, 2026-10-22, read "livraison de course à domicile à vélo" (Nice) [live check] — [BODACC API, creations](https://bodacc-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/annonces-commerciales/records?limit=1&where=familleavis%3D%22creation%22&order_by=dateparution%20desc)
- **Pappers:** pappers.fr/api returned 403 to WebFetch and curl, so pricing and free credits could not be checked [live check] — [Pappers API](https://www.pappers.fr/api)
- **INSEE 2025** (Insee Première n° 2092, 28 Jan 2026): 1,165,800 creations, +54,600 vs 1,111,200 in 2024 (+5%; 4.9% in the table) — [INSEE, Les créations d'entreprises en 2025](https://www.insee.fr/fr/statistiques/8721354)
  - Micro-entrepreneurs 758,600 (+6%), companies 301,300 (+6%), classic sole traders 105,900 (−4%, lowest since 2012).
  - Sectors, in thousands of creations:

| Sector | 2025 creations | Change vs 2024 |
|---|---|---|
| Trade | 172.6 | +11.1% |
| Specialised, scientific and technical | 170.2 | +6.2% (mainly a classification change) |
| Administrative and support | 129.1 | +11.7% |
| Transport | 112.8 | +5.7% |
| Information and communication | 75.0 | +8.2% (companies +19.6%) |
| Real estate | 39.6 | +8.6% |
| Construction | 85.6 | −3.8% |
| Finance and insurance | 29.9 | −13.9% (coding change) |

- **INSEE 2025 sub-activities** — [INSEE, 2025](https://www.insee.fr/fr/statistiques/8721354):
  - Cleaning +18%, administrative support +19%, landscaping +19%.
  - Distance selling from specialised catalogues +32% in the text; the table implies about +38%.
  - Car equipment sellers +32%, maintenance garages +15%.
  - Postal and courier (meal delivery) is the main contributor to transport growth; only about a third of these units show activity within two years.
- **INSEE 2024** (Insee Première n° 2037, Feb 2025): about 1.11M creations (+6%). Transport and warehousing +25%, administrative and support +16%, trade +6%; specialised scientific and technical about −6% and real estate about −5% [snippet] — [INSEE, créations 2024](https://www.insee.fr/fr/statistiques/8345726)
- **INSEE September 2026** (Informations Rapides n° 249, 16 Oct 2026) — [INSEE, Informations Rapides n° 249](https://www.insee.fr/fr/statistiques/9078876):
  - 119,307 seasonally adjusted creations, a record since January 2000.
  - July–September 2026 +16.0% year on year (+45,471).
  - Contributions: business support activities +12,351 (+17.4%, building cleaning +4,400); trade +10,719 (+26.3%); information and communication +10,041 (+55%); finance and insurance −15.9%.
  - Micro-entrepreneurs are about two-thirds of the monthly total.
- **Regional and departmental creation tables by sector** for 2025 are published by INSEE — [INSEE, créations par secteur 2025, comparaisons régionales](https://www.insee.fr/fr/statistiques/2134432)
- **NAF 2025** (decree of 31 July 2025) takes effect on 1 January 2027, when INSEE reassigns each company's APE code. Each company already has a future NAF 2025 code on record — [Infogreffe, NAF 2025](https://www.infogreffe.fr/NAF-2025-codes-APE-nouvelle-grille-lecture-entreprises-a-compter-de-2027); [INSEE NAF 2025 flyer](https://fna.fr/wp-content/uploads/2025/10/InseeFlyerNaf-2025.pdf)
- **UK Companies House API:** "You can make up to 600 requests within a five-minute period" per application [live check] — [Companies House, rate limiting](https://developer-specs.company-information.service.gov.uk/guides/rateLimiting)
- **UK Free Company Data Product:** "provided free of charge", monthly ("Last Updated: 01/10/2026"), a 471MB ZIP of CSV — [Companies House, Free Company Data Product](https://download.companieshouse.gov.uk/en_output.html)
  - Fields include CompanyCategory, CompanyStatus, IncorporationDate and SICCode1–4 [live check of the field-list PDF] — [field list](https://resources.companieshouse.gov.uk/toolsToHelp/pdf/freeDataProductDataset.pdf)
- **US Census Business Formation Statistics, September 2026** (released 14 Oct 2026): 534,947 seasonally adjusted business applications (+0.5% vs August), of which 147,331 high-propensity. Next release 12 Nov 2026, with an annual revision of NAICS codes and seasonal factors [live check of the PDF] — [Census BFS, current release](https://www.census.gov/econ/bfs/pdf/bfs_current.pdf). Applications by NAICS sector, September 2026:

| NAICS sector | Applications | vs August |
|---|---|---|
| Retail Trade | 110,048 | +4.7% |
| Professional Services | 78,937 | −1.7% |
| Construction | 48,078 | +0.1% |
| Other Services | 42,149 | −2.0% |
| Administrative and Support | 38,030 | +0.7% |
| Transportation | 34,792 | −0.9% |
| Health Care | 32,198 | −1.5% |
| Accommodation and Food | 26,600 | −1.7% |
| Information | 13,806 | +4.3% |

### Inferences
- **Fast-growing SMB niches in France, as seen in creations 2025–2026:**
  - Cleaning and business-support micro-firms.
  - Landscaping.
  - E-commerce (specialised catalogue selling).
  - Car-equipment trade and maintenance garages.
  - Information and communication (+55% in Q3 2026, likely including AI and freelance IT).
  - Courier and delivery (high churn).
  Each newly created micro-firm buys quoting and invoicing, scheduling, compliance and bookkeeping. A wave of new cleaning or landscaping firms is a wave of new buyers for a vertical tool.
- **Free method:**
  1. Load the StockUniteLegale Parquet (1 Oct 2026).
  2. Group by `activitePrincipaleUniteLegale` (NAF sub-class) and creation year-month for 2023–2026.
  3. Rank sub-classes by absolute and relative growth. Filter to codes where most new units are companies or employers (they pay more than dormant micro-entrepreneurs).
  4. For a candidate code, query Recherche d'entreprises with `ca_min`/`ca_max` to see how many firms already turn over, say, €200K–2M, the ones that can afford €50–200 a month.
  5. Check BODACC free-text activities to see what the firms actually do.
- **NAF 2025 will break code-level series in January 2027.** Build the 2023–2026 baseline on current NAF codes now, and map to NAF 2025 using the `activite_principale_naf25` field Recherche d'entreprises already exposes.
- **The same approach works elsewhere:** in the UK, the monthly Companies House snapshot by SIC code and incorporation date; in the US, BFS applications by NAICS sector (sector level only in the release).
- **Caveat:** micro-entrepreneur creations dominate French counts (about two-thirds), and many never trade. Discount sub-classes where creations are almost all micro-entrepreneurs.

### Gaps
- Pappers API pricing and free credits: blocked.
- The exact INSEE BDM series identifiers for monthly creations by NAF sub-class: not found. The Sirene stock file is the dependable path.
- A ranking of the fastest-growing NAF sub-classes for 2024–2026: not published in what I read, beyond INSEE's sector and sub-activity highlights. It needs the stock-file computation.
- How `finances` in Recherche d'entreprises is sourced and how complete it is (confidential accounts are excluded).
- UK incorporation statistics by SIC, and US BFS at finer NAICS levels: not checked.

## 8. Public procurement (BOAMP, TED, DECP; US USAspending, SAM.gov)

### Takeaway
Procurement data is free, open and queryable without a key: BOAMP (11,692 notices mentioning "logiciel"), TED (525 software and IT notices performed in France in seven weeks) and USAspending (awards by NAICS). The strongest money proof is award data with amounts: France's DECP, published daily under an obligation for all public buyers since 1 Jan 2024, and USAspending. Tenders show budgets exist; DECP and USAspending show what was paid and to whom.

### Cited Findings
- **BOAMP** open API (Opendatasoft), no key: 11,692 notices with "logiciel" in `objet`. Fields include `nature_libelle` (e.g. "Résultat de marché"), `titulaire`, `nomacheteur`, `descripteur_libelle`, `type_marche`, `datelimitereponse`, `code_departement` and `donnees` (full notice). Latest 2026-10-21: a licence and maintenance contract for risk software [live check] — [BOAMP API query](https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/records?limit=1&order_by=dateparution%20desc&where=search(objet%2C%22logiciel%22))
- **TED API v3:** an anonymous POST to `/v3/notices/search` worked. Query: `classification-cpv IN (72000000 48000000) AND place-of-performance IN (FRA) AND publication-date>=20260901`. It returned `totalNoticeCount` 525, with XML and PDF links per notice [live check] — [TED API v3 search endpoint](https://api.ted.europa.eu/v3/notices/search)
- **DECP, current consolidated file** under the arrêté of 22/12/2022 — [data.gouv.fr, DECP Marchés](https://www.data.gouv.fr/datasets/donnees-essentielles-de-la-commande-publique-decp-arrete-du-22-12-2022-marches):
  - Daily, Licence Ouverte v2, updated 2026-10-21.
  - Available as CSV and JSON through data.economie.gouv.fr's Opendatasoft API [live check] — [data.economie.gouv.fr, decp-2022-marches-valides](https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/decp-2022-marches-valides/)
- **DECP obligation:** since 1 January 2024, essential data of public contracts and concessions "doivent être publiées sur data.gouv.fr". "API DECP" (AIFE) publishes daily JSON files (e.g. decp-22102026…json) [live check] — [data.gouv.fr, API DECP](https://www.data.gouv.fr/datasets/api-decp)
- **The older "données enrichies" DECP dataset is now marked "[DEPRECIE]"** [live check] — [data.gouv.fr, deprecated DECP](https://www.data.gouv.fr/datasets/deprecie-donnees-essentielles-de-la-commande-publique-donnees-enrichies)
- **USAspending API**, no key: `spending_by_award` with a NAICS filter (513210 software publishers, FY Oct 2025–Sep 2026) returned awards sorted by amount (the top ones are $100M+ defense contracts). Searches go back to 2007-10-01, and bulk downloads further [live check] — [USAspending API, spending_by_award](https://api.usaspending.gov/api/v2/search/spending_by_award/)
- **SAM.gov Get Opportunities API:**
  - Needs a public API key from a SAM.gov account ("Account Details").
  - The posted-date range is limited to one year per query, with filters by NAICS (`ncode`), set-aside and notice type.
  - `award.amount` is returned when available.
  - Daily limits "are limited based on the federal or non-federal or general roles" (no number given).
  — [GSA Open Technology, Get Opportunities API](https://open.gsa.gov/api/get-opportunities-public-api/)

### Inferences
- **Money proof from procurement** = repeated small awards for the same job across many buyers. Examples: hundreds of communes each buying a cemetery-management module, school-canteen booking or a room-booking tool, each for €5–40K.
- **Fields to extract per award:**
  - Object (`objet`), CPV code, amount, duration, award date
  - Buyer type (commune, hospital, school), and supplier SIRET (to identify incumbents)
  - Number of bids, where present
- **Method:**
  1. Query DECP for CPV 48* (software) and 72* (IT services) over 2024–2026.
  2. Cluster by normalized object text.
  3. Keep clusters with many distinct buyers and median amounts under the €40K "marché à procédure adaptée" range (a bet on the threshold; check current rules).
- **Caveats:**
  - Public buyers are slow, and sales cycles follow procurement rules, which tests a solo founder's patience.
  - Many small purchases happen below publication thresholds or through central purchasing bodies (UGAP) and will not appear one by one.
  - Use procurement as proof that a budget line exists, then sell below thresholds or through resellers.
- **US equivalent:** USAspending by NAICS or PSC, plus SAM.gov opportunities with small-business set-asides.

### Gaps
- BOAMP's dataset time coverage and licence: not read.
- TED API rate limits and reuse terms: not read.
- DECP field-level completeness (amounts, CPV) after the 2024 reform: not sampled.
- France's 2026 thresholds for publication and procedures: not checked.
- UGAP and other central-purchasing data: not researched.
- SAM.gov daily limits for non-federal users: not stated.

## 9. SaaS spend benchmarks (Vendr, Spendflo, Cledara, Ramp, Brex, Zylo, Vertice, Moss)

### Takeaway
The free, monthly sources split by company size are Ramp's (AI Index on FRED, vendor rankings, Ramp Rate) and Vendr's per-vendor price pages, which have been part of Vertice since June 2026. The annual reports (Zylo SMI 2026, Vertice's inflation index, Moss for Europe, Tropic, Spendflo) are mostly behind forms and lean toward mid-market and tech firms. Moss is the only EU card-data source found, and the only one reporting micro-companies (1–19 employees) separately: they average €703 a month on AI tools. Cledara published nothing found.

(Research for this section was run by a sub-agent on 2026-10-22.)

### Cited Findings
- **Ramp AI Index:**
  - Built from card, invoice and ACH data of "more than 85,000 American businesses", free, through September 2026 — [Ramp AI Index](https://ramp.com/data/ai-index)
  - 55.9% of businesses paid for AI tools in Sep 2026: small 50.0%, medium 62.5%, large 65.7% — [Ramp AI Index](https://ramp.com/data/ai-index)
  - By industry: Information 79.9%, Construction 43.2%, Health care 42.5%, Accommodation & Food 33.0% — [Ramp AI Index](https://ramp.com/data/ai-index)
  - Among firms paying for AI, median spend is $15.70 per employee a month — [Ramp AI Index](https://ramp.com/data/ai-index)
- **The index series are downloadable free on FRED**, by size, industry and provider [snippet] — [FRED, AI adoption by Ramp small businesses](https://fred.stlouisfed.org/data/RAMPAISMB)
- **Ramp methodology note** (3 Apr 2026): 50,000+ US businesses and more than $100B of annual spend. Customers "skew high-growth and tech-forward" and are larger than most US firms — [How Ramp data works](https://econlab.substack.com/p/how-ramp-data-works)
- **"Top SaaS Vendors on Ramp"** is monthly; the Aug 2026 edition covers 70,000+ businesses. Its tables sit in a chart widget a text fetch misses — [Ramp, Top SaaS vendors Aug 2026](https://ramp.com/data/top-saas-vendors-on-ramp-aug-2026)
- **Ramp Rate** is "a free vendor directory" (302 vendors), with "most adopted" and fastest-growing lists. No per-vendor spend appeared in the fetch — [Ramp Rate](https://ramp.com/vendors)
- **Vertice announced its acquisition of Vendr** on 1 Jun 2026 [snippet] — [tech.eu](https://tech.eu/2026/06/01/vertice-acquires-vendr-to-build-ai-powered-procurement-intelligence-platform/)
- **Vendr per-vendor pages remain public.** Example (HubSpot): median annual contract $26,250, range $2,900–$75,037, based on 979 purchases, "Last updated: February 2026" — [Vendr, HubSpot pricing](https://www.vendr.com/marketplace/hubspot)
- **Vertice SaaS inflation:** 14.3% for Sep 2026 ("early data"), 12.7% Aug, 16.4% peak in Jun, from spend it manages. There is no category or company-size split on the public page — [Vertice, SaaS inflation rate](https://www.vertice.one/insights/saas-inflation-rate)
- **Zylo 2026 SaaS Management Index** (29 Jan 2026): 40M+ licenses, $75B of spend and 218 IT leaders surveyed — [Zylo press release](https://zylo.com/news/2026-saas-management-index)
  - Median SaaS spend of $9,455 per employee.
  - AI-native app spend +108% year on year.
  - Expensed SaaS spend +267%.
  - Business units control 81% of SaaS spend.
- **Moss "European SaaS & AI Spending Report 2026"**: anonymised card transactions of European companies, €302M, Jan 2024–May 2026, free behind a work-email form — [Moss](https://www.getmoss.com/vendor-market-spend)
  - Category growth, Jan–May 2026 vs 2025: AI Dev Tools +1,009%, AI Tools +309%, E-commerce +72%, HR & People +54%, Marketing +48%, Design +36%, CRM & Sales +12%, Dev Tools −20%.
  - Fast movers in May 2026 vs the trailing 3 months: Wispr +70%, GetMyInvoices +53%, Granola +46%.
  - Average monthly AI bill: €703 at 1–19 employees, €876 at 20–99, €1,534 at 100+.
- **Brex Benchmark** hub ("over 35,000 companies") lists editions up to Oct 2026, e.g. the Spring 2026 top 25 fastest-growing software vendors. Only the titles were read — [Brex Benchmark](https://www.brex.com/resources/brex-benchmark)
- **Tropic:** latest found is the 2023 SaaS Benchmarks Report (15,000+ requests, 8,000 contracts), behind a form — [Tropic benchmarks report](https://tropicapp.io/resources/benchmarks-report)
- **Spendflo:** latest confirmed is "State of SaaS Procurement 2025" (ebook) [snippet] — [Spendflo](https://www.spendflo.com/ebook/state-of-saas-procurement-2025)

### Inferences
- **Catalog:**

| Source | Latest | Access | Use |
|---|---|---|---|
| Ramp AI Index / FRED | Sep 2026 | Free | Who pays for AI, by size and industry (US) |
| Ramp vendor rankings / Ramp Rate | Aug 2026 | Free (charts) | Fastest-growing vendors on card spend |
| Vendr per-vendor pages | Feb 2026 | Free | Real contract floors and medians per vendor |
| Vertice inflation | Oct 2026 | Free headline | Incumbent price increases |
| Zylo SMI | Jan 2026 | Download page | Spend per employee, expensed spend |
| Moss (EU) | May 2026 data | Email form | EU category growth, micro-company spend |
| Brex Benchmark | Oct 2026 | Free articles | Fastest-growing vendors |
| Tropic / Spendflo | 2023 / 2025 | Forms | Category shares |

- **How to use them:**
  - A category growing fast in SMB card spend (Moss: E-commerce, HR, Marketing) plus incumbents raising prices 12–16% (Vertice) plus a low contract floor at Vendr (e.g. $2,900 a year for HubSpot) means small buyers already pay and may be under-served by a pricier tool.
  - Zylo's expensed spend (+267%) and business-unit control (81%) describe bottom-up card buying, the motion a solo founder can reach without procurement.
- **Bias:** all these datasets lean to funded, tech-forward firms with more than about 20 staff. Use them to pick categories, not to size French micro-companies.

### Gaps
- Cledara: no public report found.
- Spendflo 2026 edition: unverified.
- Productiv: no 2025–2026 data.
- Zylo per-employee averages beyond the median: snippets only.
- Ramp vendor table ranks: need a browser.
- Brex article contents: not read.
- Moss: sample count not stated, and its total (€302M) does not reconcile with its own figures (about €227M back-calculated).
- No France-only spend-per-employee data.

## 10. Other money traces: affiliate commissions, newsletter and podcast sponsorships, template sales (Etsy, Gumroad and others)

### Takeaway
Three traces show where money already flows:
- **Sponsorship prices** show which audiences are worth most. On Paved, HR newsletters cost $18.47 per 1,000 subscribers against $1.22 for lifestyle. B2B, finance and business podcasts get $40+ CPM.
- **Recurring affiliate commissions** of 20–30% are the SaaS norm, signalling high-margin, sticky categories, though rate data comes from listicles.
- **Template sales** leave the best public sales trail on Etsy: public shop sales totals, Bestseller badges and `transaction_sold_count` in the API, with estimators at $6–69 a month and screen-scraping forbidden. Gumroad shows sales only when the seller opts in, and Notion and Figma hide purchase counts.

(Research for this section was run by a sub-agent on 2026-10-22.)

### Cited Findings

#### Affiliate commissions
- PartnerStack's marketplace tracks recurring subscription charges, so partners earn on renewals [snippet] — [PartnerStack marketplace](https://partnerstack.com/marketplace)
- A directory puts typical SaaS payouts on PartnerStack at 15–40%, recurring or flat [snippet] — [UpPromote](https://uppromote.com/affiliate-directory/partnerstack/)
- 20–30% recurring is called the SaaS norm, against $50–500 one-off bounties [snippet] — [Fungies 2026](https://fungies.io/how-to-set-up-affiliate-program-digital-product-saas-2026.md)
- Examples: HubSpot 30% recurring for up to a year (180-day cookie); Semrush $50–300 per sale (120-day cookie); Pipedrive 20% [snippet] — [BotPenguin](https://botpenguin.com/blogs/best-saas-affiliate-programs)
- impact.com's brand marketplace opens only after platform approval [snippet] — [Ecommerce Paradise, 2026](https://ecommerceparadise.com/impact-com-review-2026/)

#### Newsletter sponsorships
- Paved Q3 2026 benchmarks (15 categories, 12 months, at least 20 campaigns per category), price per 1,000 subscribers: HR $18.47; Marketing $13.88; Startups $13.28; Education $7.21; Finance $7.11; Business $5.34; Tech $4.76; News $2.47; Lifestyle $1.22 — [PPC Land, 30 Aug 2026](https://ppc.land/paved-finds-hr-newsletter-ad-rates-run-15-times-higher-than-lifestyle-lists/)
- The average HR list on Paved has 24,439 subscribers, against 766,110 for lifestyle — [PPC Land](https://ppc.land/paved-finds-hr-newsletter-ad-rates-run-15-times-higher-than-lifestyle-lists/)
- beehiiv's Ad Network pays a CPM on unique opens, priced per publication; publishers need a paid plan [snippet] — [beehiiv help](https://www.beehiiv.com/support/article/17525818225431-using-the-beehiiv-ad-network)
- SparkLoop: advertisers pay $1–5 per confirmed subscriber [snippet] — [SparkLoop help](https://help.sparkloop.app/en/articles/8958147-setting-your-partner-program-cpa)
- Dupple's B2B newsletter CPMs: cybersecurity $25–60, fintech $20–45, developer $15–40, HR $10–25 [snippet; vendor] — [Dupple](https://dupple.com/learn/cpm-benchmarks-b2b-newsletters)
- Passionfroot publishes no rate card; it raised $15M on 22 Jul 2026 [snippet] — [TechCrunch](https://techcrunch.com/2026/07/22/passionfroot-raises-15m-to-expand-its-b2b-creator-marketplace-to-the-us/)

#### Podcast sponsorships
- IAB/PwC full-year 2025: US podcast ad revenue of $2.9B, +17.6% [snippet] — [IAB/PwC FY2025 report](https://www.iab.com/wp-content/uploads/2026/04/IAB_PwC_Internet_Ad_Revenue_Report_Full_Year_2025_April_2026.pdf)
- Acast 2026 guidance: pre-recorded ads $15–30 CPM, host reads $25–40, B2B, finance and business shows $40+ — [Acast](https://www.acast.com/news-and-insights/how-much-does-podcast-advertising-cost)
- The AdvertiseCast/Libsyn CPM series is no longer published; its last reading was $21.37 for a 60-second spot, Sep 2024 [snippet] — [Castos](https://castos.com/podcast-advertising-rates)

#### Etsy
- Open API v3 access levels: a Seller App for your own shop; a Personal App at "limited scale" after a review; Commercial Access reviewed manually. "Screen-scraping is not allowed" — [Etsy developer docs](https://developers.etsy.com/documentation/)
- Example rate-limit headers show 150 requests a second and 100,000 a day — [Etsy rate limits](https://developers.etsy.com/documentation/essentials/rate-limits)
- Shop endpoints return `transaction_sold_count`; listings return `num_favorers` [snippet] — [etsy/open-api changelog](https://newreleases.io/project/github/etsy/open-api/release/3.0.0-alpha-2021-05-04)
- Shop pages show a public sales tally [snippet] — [Alura docs](https://alura.io/docs/article/tracking-your-sales-on-etsy)
- The Bestseller badge reflects "high sales volume over the past 6 months" [snippet] — [Listadum](https://www.listadum.com/blog/does-the-bestseller-badge-on-etsy-actually-mean-anything)
- Estimators:
  - eRank: $0 (5 searches a day), $5.99, $9.99 or $29.99 a month, with estimated daily sales per shop and no published method — [eRank pricing](https://erank.com/pricing)
  - EverBee: free, $24.99 (billed $299 a year) or $69 a month (billed $828 a year) — [EverBee pricing](https://everbee.io/pricing)
  - Alura: $0–29.99 a month, with export and API on every plan — [Alura pricing](https://www.alura.io/pricing)
  - Marmalead: $19 a month, no sales estimates — [Marmalead pricing](https://marmalead.com/pricing)

#### Gumroad, Lemon Squeezy, Whop and template sales
- Gumroad has a per-product "Sales Counter: Show total sales on product page" setting (docs of the open-source codebase) — [Gumroad docs (Mintlify)](https://mintlify.wiki/antiwork/gumroad/features/products)
- A Lemon Squeezy marketplace listing requires at least 3 sales or $50 in total sales, then a review; the fee is a flat 30% — [Lemon Squeezy docs](https://docs.lemonsqueezy.com/help/marketplace)
- Whop's best-sellers view ranks products by monthly recurring revenue [snippet] — [Whop docs](https://docs.whop.com/algorithm)
- Practitioner data points:
  - A Notion-template business was listed in June 2025 at $50K, with about $23.4K a year in revenue and 26 templates [snippet; seller claim] — [Microns listing](https://www.microns.io/startup-listings/platform-selling-templates-for-notion)
  - Kajabi credits the template seller Easlo with $500K+ in sales (Sep 2024) [snippet] — [Kajabi](https://kajabi.com/blog/can-you-make-money-selling-notion-templates)

### Inferences
- **Affiliate.** A vendor that gives away 20–30% of revenue for 12 months expects high gross margin and retention beyond a year. A long cookie (120–180 days) means a considered B2B purchase. A $50–300 bounty is a floor on one customer's value. Favor jobs where vendors pay high recurring commissions but programs are few: crowded affiliate categories prove willingness to pay but have bid up acquisition costs.
- **Sponsorship.** Paved's ranking says employers with budgets want to reach HR, marketing and startup operators. Those are audiences whose jobs carry budgets. These prices measure what advertisers pay to reach an audience, not what that audience pays for a tool, so pair them with sections 1, 5 and 9 before calling it demand.
- **Etsy method:**
  1. Search business-workflow terms: bookkeeping spreadsheet, invoice template, client tracker, inventory, small-business planner.
  2. Through an approved Personal App (not scraping), record `transaction_sold_count` for the top shops, then again 14 days later.
  3. Sales gained × median price gives each niche's revenue speed. Cross-check with eRank.
  4. Fields to record: term, shop, sold counts at both dates, price, favorers, listing age, reviews, Bestseller badge.
- **Templates as a signal.** A template that sells shows a workflow people pay to systematize. Whether its buyers would move from a €20 template to a €20–50 monthly tool is a bet to test, not evidence.

### Gaps
- Logged-in PartnerStack or impact.com commission data by category: not accessed.
- Paved's own report URL and whether it is gated: unknown.
- No European newsletter or podcast rate benchmarks found.
- Etsy's API Terms (etsy.com/legal/api): 403.
- No official Etsy page for the "X people bought this in the last 24 hours" signal.
- No data on which business templates sell best on Etsy; it needs the measurement above.
- Not verified: Figma "used by" counts, Creative Market and Payhip sales display, what Gumroad Discover and Whop Discover show.
- No dated write-up of a founder who used Ramp, Vendr, affiliate rates or sponsorship rates to choose a niche.
