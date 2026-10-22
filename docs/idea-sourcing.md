# Idea sourcing: a fabric of ideas people already pay for

**Status:** proposal 2026-10-22, for Vlad to validate · **Evidence:** the research report
`docs/research/reports/Finding ideas people pay for.md` and its notes in
`docs/research/research_notes/Finding ideas people pay for/` (all read on 2026-10-22) ·
**Founder fit:** `founders/about_vlad.md`, private and git-ignored, never sent to an outside model.

Vlad's ask, verbatim (2026-10-22):

> Let's say I want to build a side business, that generates minimum 10k/month net revenue without
> too much hassle. How would you investigate and give me ideas? How would you come up with pains -
> and where people are OK to pay money for that? here are some of my ideas: reddit, hacker news,
> new top spenders on facebook / google (how to track them?), experiences at Dolead (ex: slack,
> emails), what else? But I want a fabric of really solid ideas. So I can choose.

This method comes before the factory. The weekly plan tests one idea; this method decides which
ideas deserve that week. It is the design input for `/factory-scout` (design §14, "later"). That
command gets built only after Vlad has judged one harvest run by hand (section 10).

## In one page

- **Start from money, not from complaints.** Complaints are plentiful and mostly unpaid. The
  harvest starts where money already moves:
  - what people pay competitors, freelancers and staff to do;
  - what a deadline forces them to buy;
  - what advertisers pay to get customers.

  Only then does it look for the pain inside those flows: people who pay and still hurt.
- **An idea is solid when four threads cross.** Money (C), pain shown in what buyers do (P), a
  route to reach buyers again and again (R), and a fit for founders with a few hours a week (H for
  hassle, F for fit and conflict). C, P and R are the triage's own letters. This method applies
  them before an idea exists, to many candidates at once.
- **10k EUR net a month is about 14–15k EUR of revenue.** That is about 72 customers at 199 EUR,
  or about 490 at 29 EUR. Below about 50 a month, retention and the support load per euro get much
  worse (section 1). So the target shape is:
  - B2B or prosumer buyers paying 150–1,000 EUR a month;
  - self-serve, or one call to sign;
  - value delivered without a live duty (reports, documents, done-for-you work run by agents).

  Two other roads reach the same number: a productized service run by agents, and buying a
  business that already earns it.
- **Your four sources, rated.**
  - *Reddit* is the richest English pain source. But since November 2025 every API use needs
    Reddit's approval, its `.json` endpoints are closed, and French SMB buyers barely use it. Use
    it to check a pain and to borrow the buyers' words, not to discover ideas.
  - *Hacker News* is free and open, but its buyers are developers.
  - *New top spenders* can be tracked in the EU for 0–40 EUR a month from official sources
    (section 4). They prove that a category pays to acquire customers, not that it would pay you.
  - *Dolead experience* is usable as memory, never as data (section 5).
- **What else, strongest evidence first:**
  - paid apps in marketplaces;
  - verified revenue and businesses for sale;
  - work people pay freelancers for;
  - deadlines with penalties;
  - search demand with its cost per click;
  - company registries, to count buyers;
  - feature requests with thousands of votes;
  - templates that sell.

  Section 3 says how to reach each one in October 2026.
- **Output: a board, not a list.** 20–30 threads, each one buyer × one job, with its evidence and
  scores. The best 3–5 are written up as intake-ready cards, each with a 48-hour test. Vlad picks
  one, and `/idea-new` takes it from there.
- **Proposed next step:** one harvest by hand (section 10). About 20 EUR cash, about 2 hours of
  Vlad's time, and a board within a week.

## 1. The target in numbers

**"Net"** means revenue minus the costs of earning it (ads, tools, fees, freelancers), before
income tax. This is Vlad's definition in his other businesses; he should confirm it applies here.
At a 70 % margin, 10k EUR net needs about 14.3k EUR of monthly revenue. The arithmetic comes from
the methods notes:

| Price per customer per month (EUR) | Customers for 14.3k | Lost per month at 3 % churn | at 6 % |
|---:|---:|---:|---:|
| 29 | 493 | 14.8 | 29.6 |
| 99 | 144 | 4.3 | 8.6 |
| 199 | 72 | 2.2 | 4.3 |
| 499 | 29 | 0.9 | 1.7 |
| 999 | 14 | 0.4 | 0.9 |

The churn columns are illustrations: the averages MicroConf published give no period.

**What the base rates say** (methods notes):

- **MicroConf's latest survey** is the 2024 edition (data from late 2023, 469–700 founders).
  - The largest bucket is under $1k of monthly revenue.
  - About a third of companies grow 1–4 % a month, and another third are flat or shrinking.
  - Companies led full-time grow 30 % faster than part-time ones.
  - Entry plans at $1,000 a month or more add about $1,073 of new revenue a month, against $316
    for plans priced $1–9.
  - It publishes no share of companies above $10k a month.
- **About 6 % of products with verified revenue earn above $10k a month.** This is a third-party
  analysis of TrustMRR data that could not be opened, so it is unverified.
- **AI products churn sharply below $50 a month** (ChartMogul, December 2025). Their median gross
  retention is 40 %, and 23 % below $50 a month. Above $250 a month they retain like ordinary B2B
  software.

**What that implies.** For a self-built product run part-time, 10k net is a top-decile outcome.
High prices and few customers are the shape that gets there with little hassle. Low prices
multiply both the customers to win and the tickets to answer.

**Three roads to the number:**
1. **Build a product.** The default the factory tests.
2. **Sell a productized service run by agents.** A fixed monthly price for a done-for-you job:
   agents do the work and a freelancer checks it. Nothing has to be built before the first sale,
   and the service can grow into software later.
3. **Buy a business.** In 2025 to mid-2026, small online businesses sold for about 2.2–3.9×
   annual profit:
   - Acquire.com's SaaS median: 3.9×;
   - Flippa's SaaS average for H1 2026: 2.47×;
   - Empire Flippers' typical deal: 2.2–2.3×.

   So 5–15k a month of profit costs roughly $140k–800k, mostly $220k–700k for SaaS. No source
   publishes whether buyers keep the revenue.

## 2. The principle: follow the money, then find the pain inside it

| Thread | The question | Letter |
|---|---|---|
| Money | Who pays for this job today, how much, to whom? | C |
| Pain | Does the buyer show the problem in actions: hours, workarounds, switching, hiring? | P |
| Route | Can we reach these buyers by name, repeatedly, at a cost the price supports? | R |
| Fit | Can the founders deliver it in a few hours a week, without a conflict? | H, F |

Evidence of money, strongest first:

1. They pay a competitor now: prices, installs, reviews, verified revenue.
2. They pay a person now: freelance gigs, job postings, agencies.
3. They must pay soon: a deadline with a penalty.
4. They pay to acquire their own customers: ad spend in their category. This is adjacent evidence
   and never enough on its own (the triage rule).
5. They keep a workaround: spreadsheets, hours, internal tools.
6. They complain.

Why money comes first:

- Practitioners judge buying pain by behaviour: past spend, existing workarounds, switching, and
  whether the person who complains is the buyer (pain notes, signal quality).
- Generic phrases are frequent and mostly off-topic. On a year of Hacker News comments, "alternative
  to" had 3,931 hits and "we pay" 925. Phrases that describe what someone did, such as "hired
  someone to" or "manually every", carry more intent per hit (pain notes).

## 3. Where each kind of evidence lives, and how to reach it (October 2026)

| Source | Proves | Access, cost, terms | What to extract | In the factory |
|---|---|---|---|---|
| Paid marketplaces | C, P, R | Atlassian Marketplace REST API: free, with installs, reviews and prices, and it sorts by top-grossing. WordPress.org API: free (active installs, daily downloads, stars, support threads). Chrome Web Store: user counts. Shopify: reviews and plans on the listing, a 1-star filter, installs through StoreCensus (free per app) | Categories where paid apps have many users and stale or poor ratings; prices; reasons in 1–3★ reviews | nothing yet |
| Verified revenue, businesses for sale | C, buy road | TrustMRR: 15,000+ startups, 3,000+ for sale, API behind a login, no bulk republication. Flippa and Empire Flippers listings are public. Acquire.com and Microns sit behind plans or NDAs | Niches earning 5–20k a month, their churn, why the owner sells | nothing yet |
| Paid labour | C, P | Codeur.com: budgets and offer counts, France. Freelancer.com: open API with budgets. Indeed Hiring Lab: trends. Restricted: France Travail's job API. Gone: Upwork RSS (since August 2024). LinkedIn forbids scraping | Tasks people pay humans to do every month, the rates, the volume | nothing yet |
| Deadlines with penalties | C (forced), timing | The calendar in the research notes: 70+ dated items, each checked on 2026-10-22 | Who must act, when, the penalty, how crowded the vendors are | the calendar file |
| Ad spend, including new top spenders | C (adjacent), R | Section 4 | Rising categories and advertisers, and the promises they pay to show | `ad_library`, `serp_ads`, `nb adsinsights` |
| Search demand | C (CPC), R | SE Ranking (keys held): volume, CPC, competition, intent, 12 months, who bids. Keyword Planner needs an Ads account with billing | Volumes and CPCs of "X logiciel", "X software", "alternative à X", "X prix" | `keyword_volume`, `serp_ads` |
| Reviews of paid tools | P with C | Shopify, WordPress.org and Google Play are open. G2, Capterra, TrustRadius and Trustpilot block automated reads, and G2's terms forbid them: read by hand | Why customers switch: a missing feature, a price rise, too complex for a small user | nothing yet |
| Feature requests | P (C on paid tools) | Atlassian's public Jira, sorted by votes with no login: 51,171 open suggestions, the top ones with 2,400–2,850 votes. Discourse forums (Shopify Community, Make, Spiceworks). GitHub issues sorted by 👍 | Old, heavily voted requests that were never built, on paid products | nothing yet |
| Communities | P, R | Reddit: any API use needs approval since November 2025, `.json` closed, RSS works, the Arctic Shift archive is free but carries no commercial licence. HN through Algolia: free, 10,000 requests an hour. F5Bot and Syften alerts: 0–120 USD a month. LinkedIn and French Facebook groups (the largest has about 102,700 members): by hand | The buyers' words, their workarounds, people to answer | `reddit_mentions`, `hn_mentions` |
| Company registries | Counting buyers | SIRENE: free API and monthly files. API Recherche d'entreprises: no key, filters by NAF code and revenue. BODACC. INSEE counts 2025 creations at a record 1,165,800, and Q3 2026 at +16 % year on year, information and communication +55 %. NAF codes change on 2027-01-01 | How many buyers of a kind exist, which kinds are growing | nothing yet |
| Public spending | C | BOAMP, TED, and DECP (contracts awarded, with amounts, published daily since 2024) | Budgets for software and services. Sales cycles are long, which is hassle | nothing yet |
| Templates that sell | C | Etsy: shop sales are public, and the API has `transaction_sold_count`. Gumroad shows sales only when the seller opts in | Business workflows people pay to systematise | nothing yet |
| SaaS spend benchmarks | C per category | Ramp AI Index, Vertice (ex-Vendr) price pages. Moss (EU): micro-companies average 703 EUR a month on AI tools | Budget lines per category and company size | nothing yet |
| The founders' experience | P firsthand, R through the network | Recall sessions and the itch ledger (section 5) | Pains paid for in hours | `founders/` (private) |

## 4. New top spenders: how to track them, and what they prove

**What the signal means.** An advertiser whose exposure keeps rising for 6–8 weeks has found
customers worth more than they cost at today's prices. That supports three uses:

- **The category pays to acquire customers.** This is a C signal, but only adjacent.
- **The advertiser is a buyer with a budget.** Tools that protect or improve that spend can be
  sold to them (pattern 7).
- **Their ads are free research.** They show the promises and pains that convert in that market.

On its own it never makes a thread (the triage rule for adjacent advertising).

**How to track it, by region** (ad-spend notes §1–7 and §10):

| Scope | Source | What it gives | Cost and access |
|---|---|---|---|
| EU, any category | Google's public BigQuery dataset `bigquery-public-data.google_ads_transparency_center` (`creative_stats`) | Every advertiser in the EEA. Per country: first and last shown dates (1-day lag) and impression bounds (90-day lag), by surface. 56 topics | Free within BigQuery's 1 TiB a month (a weekly France query scans about 30–80 GB). Needs a personal Google Cloud project |
| EU, any category | Meta Ad Library API | Every ad delivered in the EU, with `eu_total_reach` and reach by country, age and gender. No spend for commercial ads. Weekly snapshots give Δreach per page | Free. Needs identity confirmation and a developer app |
| EU, B2B | LinkedIn Ad Library | Estimated impressions and the share per country, for EU-targeted ads | Gated API, or SearchAPI |
| EU | Snapchat Ads Gallery API; Microsoft Ad Library API | Exact impressions per country (Snapchat); impression bands (Microsoft) | Free, no key |
| EU | TikTok Commercial Content API | Daily ad counts per advertiser, and users reached | Its research-tool terms forbid commercial use; get TikTok's answer in writing first, otherwise use SearchAPI's scraped library |
| US | SE Ranking (monthly), SearchAPI snapshots (weekly) | Who started bidding on Google, and estimated traffic cost; active and new Meta and Google ads per page. No platform publishes US exposure for commercial ads | Keys held; SearchAPI's quota resets 2026-11-05 |
| The employer's categories | AdsInsights through NeuralBox | Reach per country × category, kept over time. Its query engine ranks by reach gained over 1d, 1w or 1m, and has a history section (NeuralBox's tool README, read 2026-10-22). `nb adsinsights` uses only `sort=all` today | About 0.15–0.30 USD a call. Keep aggregated conclusions only (design §4). Covers only the categories the employer tracks, which is exactly where a side business would conflict |
| Ready-made | Trendtrack (~62 USD/month, EU Meta reach and spend estimates, 10 brands), Semrush Advertising (€94.94/month, billed yearly), SerpApi Transparency API ($25 per 1,000) | The same signals, packaged | Panel-based spend estimates start at $129 a month (AdClarity); Sensor Tower and MediaRadar are enterprise contracts |

**Turning exposure into euros:**

- The formula is ΔEU reach × frequency × CPM ÷ 1,000, with frequency 1.5–2.5. Meta's CPM in 2026
  is about $7–9 in France and $16–23 in the US.
- Always give the result as a range: no platform publishes commercial spend.

**Pitfalls** (ad-spend notes §10):

- **Exposure figures exist only for the EU.** US rankings rest on proxies.
- **Google's impression figures lag 90 days.** Its creative counts are fresh.
- **"Advertiser" is often the wrong entity.** It can be an agency or a reseller, and affiliates
  muddy every category. Resolve each advertiser to its landing domain before ranking.
- **Long-running ads do not prove scaling.** Retargeting and brand ads run long without scaling,
  and dynamic and catalogue ads multiply the ad count. About 5 % of creatives take 55 % of spend
  (Motion, 2026). Longevity and creative velocity are proxies for scale, not for profit.
- **The libraries are incomplete, unevenly.** A May 2026 audit by ÖIAT (an Austrian research
  institute) found none of Meta, TikTok, Google or Snapchat fully compliant. Ads vanished from
  Meta's library, and most Snapchat ads were missing from its archive. Compare advertisers within
  one platform, never across platforms.
- **Q4 distorts everything.** Black Friday CPMs and creative bursts.
- **Rising spend is not profit.** It can be funded growth or a failing test. Keep only "still
  rising after 6–8 weeks, with old ads surviving".

**Recommendation.**

- Run France and the EU first:
  - Google BigQuery by topic: new entrants, and how fast each advertiser launches new creatives;
  - Meta's API for the change in reach;
  - LinkedIn for B2B;
  - AdsInsights movers as a cross-check inside its categories.
- For the US, use SE Ranking's "who started bidding" only.
- The output per topic: the 20 advertisers whose exposure or creative velocity jumped, with links.
  Each becomes a money signal on a thread, never a thread by itself.

## 5. Experience as a source, inside the boundary

**Recommendation: do not mine Dolead's Slack, mail or documents for this, by hand or by agent.**

1. **The duty to the employer.** An employee owes loyalty and confidentiality to the employer for
   the life of the contract (Code du travail, art. L1222-1: the contract is performed in good
   faith). A contract can add exclusivity, an assignment of what the employee invents, or a
   non-compete clause. Have a lawyer read Vlad's contract before the side business earns its first
   euro.
2. **This repo's rules.**
   - No company content lands here (design §4 and the anti-goals).
   - Private context never reaches an outside model, and an agent reading Slack would be one.
3. **Practical.** The pains in those channels belong mostly to the employer's own market: lead
   generation and ad buying. A side business built on them competes with the employer or sells to
   its clients. The conflict filter (section 7) would remove most of them anyway.

**What keeps the insight without the data:**

- **A recall session per founder, 30 minutes, from memory, in their own words.** List the jobs you
  have seen companies pay for and resent:
  - vendors renewed with a sigh;
  - tools built in-house because nothing fit;
  - tasks handed to freelancers every month;
  - incidents that cost money.

  Write the list in `founders/` (private). Then generalize each one ("companies of 50–300 people
  that buy ads") and verify it in public sources (sections 3–4) before it becomes a thread.
- **The itch ledger.** The founders' own recurring chores, above all the ones they already
  automated, because each was paid for in hours. Vlad's list is in `founders/about_vlad.md`.
  - The question is not "is it painful?": it is.
  - The question is "how many others have it, and what do they pay today?", and the money sources
    answer it.
- **The cofounder's own ledger**, in `founders/about_<name>.md`.
- **Tools built at an employer belong to the employer.** The only road to one is an explicit
  agreement (a spin-off or a licence). That is a conversation Vlad leads, not a harvest.

## 6. Weaving: signal → thread → card → board

- **Signal**: one observation, with these fields:
  - date, source, URL;
  - buyer (role and company type) and the job;
  - kind (C, P or R) and strength (0–2);
  - the evidence, verbatim: a number or a quote;
  - geo, language, and the cost of collecting it.
- **Thread**: one buyer × one job. It holds:
  - its signals and its scores (section 7);
  - a price hypothesis, and the number of customers needed at that price;
  - the conflict check;
  - the pattern that produced it (section 8).
- **Card**: a woven thread, written up for intake:
  - a pitch in the founder's voice;
  - the evidence, linked;
  - the 10k arithmetic;
  - one 48-hour test.

  Only cards go to `/idea-new`.
- **Board**: one row per thread, with these columns:
  - slug, buyer, job;
  - P, C, R, H, F, conflict;
  - status: seed → harvested → woven → carded → picked → in the factory → verdict;
  - the next action.

Proposed home, once built: `scout/` (`signals.jsonl`, `threads/`, `board.md`, `costs.jsonl`,
`learnings.md`). For the pilot, plain markdown files in `scout/`.

## 7. Scoring: solid, low-hassle, worth 10k

**P, C, R**, as in the triage (0–2, or U for not looked at):

| Letter | 2 | 1 | 0 |
|---|---|---|---|
| C | They pay for this job today; a price and a payer have been seen | Adjacent money: ad spend in the category, a budget line, a deadline with a penalty | Nothing found after looking |
| P | Buyers show the problem in actions, from two sources | Said, or seen in one source | Nothing found |
| R | Both an unpaid route to named buyers (a community, a marketplace, a list) and a paid route whose CPC the price supports | One of the two | Neither |

**H, hassle.** Eight factors, each scored 0, 1 or 2:

| Factor | 0 | 1 | 2 |
|---|---|---|---|
| 1. Customers needed at the price | ≤ 75 | 75–300 | > 300 |
| 2. Setup per customer | none | one call | an integration project |
| 3. Live duty | none | business hours | 24/7: an outage costs the customer money now |
| 4. Liability | none | handling personal data | advice, money handling, or a regulated outcome |
| 5. Sales cycle | self-serve | one call | procurement or a security review |
| 6. Platform dependency | several channels | one marketplace | one API whose owner can cut you off |
| 7. Production treadmill | none | monthly | weekly human production |
| 8. Two-sided or physical | no | partly | yes |

A thread is **low-hassle** when it scores no 2 on factors 3, 4, 5 or 8 and at most one 2
elsewhere. Vlad can override that, writing down why.

**F, fit.**

- 2: the idea uses at least one founder edge, and a founder knows the buyer firsthand.
- 1: one of the two.
- 0: neither.

The edges are paid acquisition, ad intelligence, agents in production, French and Romanian small
business admin, and affiliate marketing.

**Conflict.**

- **none**
- **check**: same buyers as an employer or another business a founder owns, but a different job.
  A written check is needed.
- **blocked**: it competes with an employer, sells to the employer's clients what the employer
  sells them, or needs the employer's data, tools or code.

**Woven (solid)** means all of the following:

- C ≥ 1 and P ≥ 1, from independent sources;
- R ≥ 1;
- low-hassle;
- conflict not blocked;
- the customers needed at the price are at most 1 % of the buyers counted (registries, installs,
  keyword volumes). The 1 % is a bet, to calibrate.

**Ranking.** Rank by C first, because money is the scarce signal. Then P + R, then F. Then timing:
a deadline 6–18 months away moves a thread up. H breaks ties. This is not a weighted sum: an order
is harder to game.

## 8. Ten patterns that turn a thread into an idea

| Pattern | What triggers it | Money to look for | The usual shape | The trap |
|---|---|---|---|---|
| 1. Paid labour → software | Recurring gigs or job ads for the same task | Rates × volume | Done-for-you at a monthly price, delivered by agents with a human check; self-serve later | People who buy humans may want humans; quality liability |
| 2. Unbundle a paid incumbent | Many 1–3★ reviews from small customers ("too complex", "too expensive for us") | The incumbent's prices and installs | The one workflow small users need, at a third of the price | The incumbent's free tier |
| 3. Geography | A product scaling spend or revenue in the US or UK with no French- or EU-compliant equivalent | Its revenue or spend | The local version, with local rules and integrations (French tax portals, approved e-invoicing platforms, French banks) | Language alone is no moat; they localize next year |
| 4. Deadline wave | An obligation with a date and a penalty | Penalty × firms in scope | The cheapest compliant path for the long tail, done for them | Crowding (French e-invoicing has 130–156 approved platforms, some free); dates slip |
| 5. Marketplace gap | Demand (installs, reviews) meeting weak supply (stale or poorly rated apps) | Installs × price; top-grossing rank | A rebuild, with the reviews as the spec | Fees and policy; one platform |
| 6. Orphaned users | A sunset, a forced migration, a price rise | What they paid before | A migration tool or service, then the cheaper alternative | One-off demand; the window closes |
| 7. Sell to the spenders | Advertisers whose spend is rising (section 4) | Their ad budgets | A tool that protects or improves that spend | Conflict when the spenders are an employer's clients; a crowded market |
| 8. The machine | Buyers searching with intent, plus cheap supply that has no distribution | The price gap | Detect from outside → instant price → cheap delivery → markup | The cheap supply already advertises (v1's Joomla lesson) |
| 9. Your own itch, priced | A chore a founder automated | What others in the same position pay today | The founder's agent, productized | n = 1 until C is found |
| 10. Template → tool | Spreadsheets or templates selling for a business workflow | Sales × price | The tool those buyers grow into | Template buyers are price-sensitive; a bet to test |

The calendar's best ratios of forced demand to vendor crowding are examples of pattern 4, still to
be verified as threads (forced-change notes):

- vulnerability reporting under the Cyber Resilience Act for small manufacturers (since
  2026-09-11);
- green-claims checks for web shops (EU-wide since 2026-09-27; France has not transposed it);
- certificate renewal for devices that cannot renew themselves (100-day certificates from
  2027-03-15), sold through managed-IT providers;
- packaging conformity files for small brands;
- solar-canopy obligations for French car parks;
- deforestation due-diligence filings for micro importers (2027-06-30).

French e-invoicing is the largest forced change and the most crowded: SMEs must issue e-invoices
from 2027-09-01, and about 2 million of some 10 million firms in scope had declared a receiving
platform.

## 9. Premises to settle before the first harvest

1. **"A new business is the fastest road to 10k a month."** Not necessarily: a business a founder
   already owns, a spin-off agreed with the employer, or a purchase may be faster.
   *Recommendation:* write down the baseline to beat (private numbers go in `founders/`), and put
   the buy road on the board as a thread type, scored the same way.
2. **"Low hassle and 10k from scratch, part-time."** The base rates make it a top-decile outcome
   (section 1). *Recommendation:* make "150 EUR a month or more, 100 customers or fewer" a hard
   filter, or accept more hassle. Low price and low hassle together is not on offer.
3. **"Reddit and Hacker News find ideas."** They find words, workarounds and people to answer, and
   rarely money. *Recommendation:* use them only on threads that already have C ≥ 1.
4. **"Mine Dolead's Slack and email."** No, for the reasons in section 5. *Recommendation:* recall
   from memory instead.
5. **"More ideas is better."** v1 died of throughput, not of a shortage of ideas: three ideas in
   ten weeks, none reached paid traffic (design §1). *Recommendation:* the board can hold 30
   threads, but at most three cards a week go to Vlad, each with its 48-hour test ready.
6. **"An AI can tell us if an idea is good."**
   - Synthetic AI respondents fail as validation: they are shallow and eager to please (Nielsen
     Norman Group).
   - No practitioner method has a controlled study behind it. The only randomized evidence backs
     the generic "state hypotheses, test them, evaluate" approach: an Italian trial (2020) and a
     759-firm replication (2024). That is what the factory does.
   - *Recommendation:* agents harvest and weave; only money tests decide.

## 10. The first harvest, by hand (the pilot)

**Goal:** within a week, a board of 20–30 threads and 3–5 cards, so that Vlad judges the method on
what it produces before anything gets built.

| # | Step | Who | Cash | Founder time |
|---|---|---|---|---|
| 1 | Recall sessions and itch ledgers, written in `founders/` | Vlad, the cofounder | 0 | 2 × 30 min |
| 2 | **Money harvest**:<br>• marketplaces: Atlassian top-grossing, WordPress, Chrome, Shopify through StoreCensus<br>• revenue and sale listings: TrustMRR, Flippa, Empire Flippers<br>• paid labour: Codeur.com, Freelancer.com<br>• the calendar's best-ratio deadlines | agent | 0–10 EUR | 0 |
| 3 | **Spend radar**, run once:<br>• Google BigQuery for France, by topic<br>• AdsInsights movers: 1 month, category and company tiles, FR and US<br>• SE Ranking: who started bidding on seed keywords | agent; Vlad creates a personal Google Cloud project | 2–5 EUR | 10 min |
| 4 | **Weave**: signals into threads, then pain checks, only on threads with C ≥ 1:<br>• Arctic Shift and Algolia<br>• Shopify and WordPress reviews<br>• Atlassian Jira votes | agent | 0 | 0 |
| 5 | Score; write the best 3–5 as cards | agent | 0 | 0 |
| 6 | Review the board; pick 1–2 for `/idea-new` | Vlad (and the cofounder) | 0 | 60 min |

**Total:** 20 EUR cash at most, about 2 hours of founder time.

**Decisions for Vlad before it runs:**

- **Where scouting costs are logged.** The factory logs costs per idea, and scouting has no
  ledger.
  - *Recommendation:* for the pilot, a `scout/costs.jsonl` written in the same line format.
  - Later, `factory costs` learns a `scout` ledger. An `_scout` idea is not the answer: the board
    would list it, since only `_fixture` is hidden.
- **A personal Google Cloud project** (BigQuery's free tier), never the employer's.
- **Meta's Ad Library API** needs identity confirmation and a developer app on a personal account.
  That belongs in `/factory-setup` (D11). Until then, the pilot skips Meta, or uses SearchAPI once
  its quota resets on 2026-11-05.
- **AdsInsights**: aggregated conclusions only (design §4). Its categories are the employer's, so
  the radar reads them as a map of where not to compete, and of who might buy tools.

**What Vlad gets:**

- `scout/board.md` and 3–5 cards;
- the pilot's own learnings: which sources produced money signals, and at what cost.

Then he decides: build `/factory-scout`, change the method, or stop.

## 11. What gets built after the pilot, if Vlad validates it

- **`/factory-scout`**: weekly and agent-run, with its own time and cash cap. It writes signals,
  updates the board, and proposes three cards at most. It goes through a builder check before it is
  built, and the design's §14 is updated.
- **Tools**, each with `--dry-run`, cost logging and tests:
  - `ads_movers`: BigQuery topics for FR/EU, an AdsInsights movers mode, SE Ranking's new bidders;
  - `marketplace_scan`: Atlassian, WordPress, Chrome, StoreCensus;
  - `listings_scan`: TrustMRR, Flippa, Empire Flippers, keeping conclusions only, as their terms
    require;
  - `labor_scan`: Codeur.com, Freelancer.com;
  - `registry_count`: API Recherche d'entreprises;
  - a dated deadline calendar, refreshed monthly;
  - the `scout/` ledger.
- **Calibration.** Every card that reaches a verdict records the sources that fed it. After ten
  verdicts, a source that never fed a PASS is dropped.
