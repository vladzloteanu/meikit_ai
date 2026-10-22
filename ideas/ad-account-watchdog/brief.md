# Brief — Ad Account Watchdog

Triage of 2026-10-22, 11:43 to 12:31 (48 minutes), 0.05 EUR cash.
New research files: `research/reddit_mentions_20261022-114801.json`,
`research/pricing_scan_20261022-115631.json`. Reused from the intake:
`research/reddit_mentions_20261022-095725.json`, `research/reddit_mentions_20261022-100611.json`,
`research/hn_mentions_20261022-095311.json` (HN not rerun: agency owners do not post there).

Coverage:
- Reddit, through the Arctic Shift archive: full text, comments and subreddit rules of r/FacebookAds,
  r/PPC and r/agency. Reddit itself returns 403 to the session's fetchers and is blocked by the
  browser extension.
- LinkedIn: the #MCCGoogleAdsHijack search, read signed in, plus one web search for a sample of
  agency founders.
- The session's web search for offers, substitutes and trade press.
- The Google Ads Transparency Center, read by hand (hacked.com, US).
- The Google Ads API (v26) and Meta Marketing API references, read by a subagent with no private
  context; the two decisive rows were re-checked by hand.

Not covered:
- The SERP and ad-library tools: SearchAPI's monthly quota is used up (HTTP 429).
- The Meta Ad Library (redirected to a sign-in page, not used) and the LinkedIn Ad Library (403).
- Facebook groups, Slack communities and X.
- The other networks of the pitch's "etc." (TikTok, LinkedIn, Microsoft).
- "MCC hacked" in r/PPC, r/googleads and r/agency (skipped by the archive's throttle).

## Summary

The buyer was seen acting:
- An agency caught a takeover of its Meta Business Manager in which "dozens" of client accounts got
  $20,000/day campaigns, and found a planted system user (#1).
- A portfolio manager has chased a $10,061.30 refund since June (#2).
- An agency founder spent three weeks and over two dozen tickets trying to get a hijacked Google
  Ads MCC back (#6).

What is sold today:
- Recovery is sold and advertised: hacked.com charges $990 per accepted business case ($1,499
  regular), and its Google ads were last shown 2026-10-21 (#12, #13).
- For agencies, the Google-side detection is a €170 one-time change-alert script (#14). Change
  history comes bundled in a $1,000/month strategy plan (#15).
- No paid offer for takeover prevention or monitoring was found for this buyer.

The route: four agency-side threads in r/FacebookAds in the last 30 days, open for replies. The
sub's rules forbid promotional links, not useful replies.

P 2, C 1, R 1, gate **PASS**.

## Decisions for the challenge

### Buyer and trigger

- **Supports:** #1, an agency holding "dozens" of client accounts in one compromised Business
  Manager. Also #2 ($10,061.30 spent on a client's account) and #6 (an agency MCC, owner removed).
  The trigger is a takeover of the agency's own Business Manager or MCC, whose blast radius is
  every client.
- **Contrary:**
  - Most of the incident volume is small operators: 7 of 28 deduplicated incidents are on the
    agency or freelancer side; the rest are small businesses and individuals (§ Complaints).
  - #4 and #5 are a freelancer and a consultant with one client each.
  - #7 shows the advertiser, not the agency, bearing the damage of an agency's forgotten MCC link
    (over €40,000 claimed). The payer could be the advertiser, watching its agencies.
- **Unresolved:** the posters' roles. Owner or staff, and agency size, are not verified: the
  records are usernames, with no profile.
- **Consequence:**
  - If the burned agency owner is the buyer, the route is post-incident threads and MCC-hijack
    posts.
  - If it is the advertiser, the offer becomes "watch who your agencies left in your accounts",
    with another page and another channel.

### Job and framing

- **Supports:**
  - #3 asks who deleted the ads, and when: the change log.
  - #1's attacker planted a system user, found by hand after the fact. A reply in that thread warns
    that attackers add users with near-identical names.
  - #7 is a 22-month-old manager link nobody revoked: access drift, as the intake's second opinion
    said.
  - #1's $20,000/day budgets are exactly a budget-jump alert.
- **Contrary:**
  - In #4 and #5 the attacker used an existing staff or freelancer login, with no new user and with
    "2FA and allowed domains" in place. A new-user alert misses these; only a spend or new-campaign
    alert catches them.
  - The platforms already cover part of the job for free (#18, #19): Google's multi-party approval
    and its 2-step-verification mandate for sub-accounts, and Meta's Security Center checklist.
  - Every purchase and ad observed is recovery, after the breach (#12, #13).
- **Unresolved:** whether "detected at the next poll" is worth a monthly fee. That means about 3
  minutes for Google budgets, tens of minutes for Google access at 50 accounts on Basic API access,
  and an undocumented delay on Meta. The rival frame is a recovery or rapid-response promise.
- **Consequence:** two framings for the page, its price and the moment of purchase:
  - "access drift and spend-anomaly detection", sold before the breach;
  - "rapid response when it happens", sold at or after the breach.

### Unpaid channel

- **Supports:** `reddit_reply` in r/FacebookAds:
  - #1 to #4 are four agency-side threads posted between 2026-09-30 and 2026-10-05, all open.
  - #1 drew 25 comments, so help-seeking is active.
  - The rules snapshot allows content that brings value and bans links to services (§ Route).
- **Contrary:**
  - The yield is low: about one agency-side thread a week at best, from a burst in early October
    (counts are lower bounds).
  - r/PPC treats threads of services as spam, and r/agency bans unsolicited sales DMs.
  - Offering a product to someone mid-incident can read as ambulance-chasing.
  - LinkedIn's #MCCGoogleAdsHijack gives two agency founders in ten months (#6 and one comment).
    Untriggered agency founders are plentiful, but free accounts reportedly send only about three
    to five personalized invitation notes a month.
- **Unresolved:** how many replies turn into conversations; whether moderators would approve one
  value post (a post-incident lockdown checklist).
- **Consequence:** if fewer than one reply in three becomes a conversation, the test falls back to
  LinkedIn outreach to agency owners with no trigger. That is the weakest framing under the
  intake's premise 5.

### Price and purchase unit

- **Supports:**
  - Buyers pay hundreds of dollars per incident after a breach: hacked.com's $990 business case
    ($1,499 regular), its $149 assessment call and an optional $899/year support plan (#12).
  - One incident costs far more than 599: $10,061.30 (#2), $20,000/day budgets (#1), €40,000
    claimed (#7).
- **Contrary:**
  - The only agency-targeted detection offer is a €170 one-time script (#14).
  - Change history with before and after is free on The Ad Spend's Starter plan, for teams running
    their own accounts. Agency management needs All Access, a $1,000/month strategy plan at $10K of
    monthly ad spend (#15).
  - An agency gives a security-inclusive Meta ads audit away as lead generation (#17).
  - The one buyer budget found for recovery plus lockdown is $10–30 (#16; adjacent: Pakistan,
    unknown role).
  - The platform features are free (#18, #19).
- **Unresolved:**
  - whether anyone pays monthly for prevention;
  - the audit's attach rate;
  - whether 59 EUR/month per workspace is read against free tiers and €170 scripts or against a
    $10K incident.
- **Consequence:** the challenge chooses between Vlad's shape (an optional 599 audit plus
  59/month), a paid one-shot lockdown audit (closest to the per-case fees that sell today) and a
  rapid-response retainer. The ten-burned-owner test should put both the audit and the month in
  front of each owner.

## Evidence records

Retrieved 2026-10-22. Reddit texts are from the Arctic Shift archive (`api/posts/ids`,
`api/comments/search`); their links are the original threads.

| # | Source, event date | Buyer role, geo | Job | Action | Class | Fit | Independent of | Limitation |
|---|---|---|---|---|---|---|---|---|
| 1 | [r/FacebookAds 1wyf0tq](https://www.reddit.com/r/FacebookAds/comments/1wyf0tq/urgent_business_manager_hacked_hackers_set_20kday/), 2026-10-05, 25 comments | agency ("our agency's Meta Business Manager"), geo unknown | regain control of client accounts | caught it "quickly"; one campaign per client account at $20,000/day; found a "sketchy System user"; could not set spending limits: "we don't have access to billing settings" | behavior | direct | 2–7, 10 | poster's role in the agency and its size unknown; actual spend unknown |
| 2 | [r/FacebookAds 1wvf9s4](https://www.reddit.com/r/FacebookAds/comments/1wvf9s4/meta_says_a_10k_refund_for_a_hacked_portfolio_was/), incident 2026-06, post 2026-10-02 | manages a Business Portfolio for a client, geo unknown (USD) | recover fraudulent spend | refund case since June; Meta said the full $10,061.30 was processed 2026-09-16, not received | measured cost + behavior | direct | 1, 3–7, 10 | agency or freelancer not stated; net unknown |
| 3 | [r/FacebookAds 1wu5q0h](https://www.reddit.com/r/FacebookAds/comments/1wu5q0h/can_deleted_meta_adsad_sets_be_recovered_after_a/), 2026-09-30 | agency ("our agency's Meta account") | recover deleted ads, know who did it | asks whether deleted ad sets can be restored and who deleted them, and when | complaint + behavior | direct | 1, 2, 4–7, 10 | loss not quantified |
| 4 | [r/FacebookAds 1wwvaro](https://www.reddit.com/r/FacebookAds/comments/1wwvaro/stuck_in_2fa_loop_on_one_specific_business/), 2026-10-03, 11 comments | consultant managing one client's account (three people on it) | regain control | the hacker used a staff member's existing login, "not adding another user"; stuck in a 2FA loop | behavior | direct (small) | 1–3, 5–7, 10 | contrary to a new-user alert |
| 5 | [r/PPC 1valcyt](https://www.reddit.com/r/PPC/comments/1valcyt/google_ads_account_hacked_and_suspended_due_to/), 2026-07-30 | freelancer, client's Google Ads account | regain and appeal | a campaign started from the freelancer's own Workspace login; "Almost $500 lost"; 2FA and allowed domains were on; account suspended, appeal | measured cost + behavior | adjacent (freelancer) | 1–4, 6, 7, 10 | the only Google record in the Reddit sweeps |
| 6 | [LinkedIn #MCCGoogleAdsHijack](https://www.linkedin.com/search/results/all/?keywords=%23mccgoogleadshijack), post 2025-12-01, incident 2025-11-15 | founder/director of a marketing agency, Google Ads Partner for over a decade, geo unknown | recover the agency's MCC | secured every client account; "over two dozen support tickets"; MCC not restored after 3 weeks; original owner removed | behavior | direct | 1–5, 7, 10 | older than 30 days; loss not stated; the search needs a signed-in view |
| 7 | same LinkedIn search, post 2026-02-04, incident 2025-12-13 | advertiser (owner of a small SEO business), NL | stop and recover after a breach via an agency's MCC | link left open 22 months after a rejected proposal; found the fraud themselves, blocked payment methods; "over €40,000 in damages" | measured cost (claimed) + behavior | adjacent (advertiser, outside US/GB) | 1–6, 10 | claimed damages, not verified |
| 8 | comment in #1's thread, 2026-10-06 | advertiser or agency, unclear | recover spend | hit twice in 3 years; full refunds, "in approx. a year" | behavior | adjacent | 1–7 | role unclear |
| 9 | [r/FacebookAds 1p2i5ak](https://www.reddit.com/r/FacebookAds/comments/1p2i5ak/ad_agency_holding_meta_ads_account_hostage_please/), 2025-11-20 | e-commerce owner, an agency's client | prevent a repeat | after a hack, let the agency create and host the ad account | behavior (prevention) | adjacent (small business) | 1–8 | one case; the agency became the security holder |
| 10 | [Agency Growth Podcast ep. 071](https://blubrry.com/1984156/119043225) show notes, July (year not shown) | agency host | recover the agency's ad account | personal profile tied to every client account; $30,000 in two days on the agency's own account (later episode notes); recovery with Hacked; partnership with Aura afterwards | measured cost + behavior | direct | 1–7 | read through search snippets only (page 503); date and any payment to Hacked unknown |
| 11 | the two sweeps (§ Complaints) | mixed | — | 26 deduplicated incidents | count | — | — | lower bounds |
| 12 | [hacked.com Meta recovery](https://hacked.com/meta-business-portfolio-recovery/), page "reviewed 2026-08-27"; `research/pricing_scan_20261022-115631.json` | seller → businesses | recovery | $149 sale ($249) 50-minute call to review ownership and admin access; $990 sale ($1,499) business case, a fixed fee per accepted case with 12 months of follow-up; optional $899/year security support | offer | adjacent (recovery) | 1–11 | no agency pricing; prevention not promised |
| 13 | [Google Ads Transparency Center, hacked.com, US](https://adstransparency.google.com/?region=US&domain=hacked.com), inspected 2026-10-22 | verified advertiser Hawkfish AS | recovery | 17 ads, any time; ["Been Hacked? What to Do First to Protect Your Accounts"](https://adstransparency.google.com/advertiser/AR17548090336742473729/creative/CR06074163691710840833?region=US) and ["Recover Your Meta Account - We can recover your business"](https://adstransparency.google.com/advertiser/AR17548090336742473729/creative/CR06405353507578183681?region=US), text ads, both last shown 2026-10-21, to hacked.com | ad record | adjacent | 12 (same seller) | network shown as Google only; dates only for the two inspected |
| 14 | [Gumroad: change-history alerts for Google Ads manager accounts](https://nilsrooijmans.gumroad.com/l/change-history-alerts), live 2026-10-22 | seller → MCC holders (agencies) | know when someone changes a client account | €170, one-time purchase (script plus installation instructions); framed as change control (clients, interns, auto-applied recommendations), not security | offer | direct, partial (Google edits only; no access, billing or Meta) | 12, 13 | sales count and page date not shown |
| 15 | [The Ad Spend pricing](https://theadspend.com/pricing), read 2026-10-22 | seller → in-house teams and agencies | change history and alerts | Starter free (waitlist) with "every change, with the before and the after", threshold alerts, Google, Meta and 5 more networks; no agency management on Starter; All Access $1,000/month at $10K of monthly spend, then a share of spend, with agency management | offer | adjacent (security not the frame) | 12–14 | the vendor blog's "about every six hours" check is not on this page |
| 16 | [Freelancer.com.au project](https://www.freelancer.com.au/projects/facebook-marketing/recover-hacked-facebook-business-manager), posted about 2026-09 | a client in Lahore, Pakistan | recovery plus lockdown | budget $10–30 to regain admin, remove unknown users and payment methods, write a breach timeline and set 2FA; 5 bids averaging $82 | buyer spending | adjacent (geo, role, recovery) | all | tiny budget; listing status inconsistent |
| 17 | [Spilno free Meta ads audit](https://spilnoagency.com.ua/en/free-meta-ads-audit), via web search | agency → advertisers | audit including account security | free 48-hour audit on read-only access, used as lead generation | offer (free) | adjacent | all | snippet only |
| 18 | [Jon Loomer, Meta audit checklist](https://www.jonloomer.com/meta-ads-audit-account/), modified 2025-03-06 | platform feature, through a consultant | audit who holds the keys | Meta's Security Center in the Business Portfolio flags dormant ad accounts, users with possible malware, users idle 90+ days, missing 2FA, a trusted domain, two admins | free substitute | direct substitute (Meta audit) | all | consultant's page; Meta's help page did not render |
| 19 | [Google: multi-party approval](https://support.google.com/google-ads/answer/16891189) (no date); [API guide](https://developers.google.com/google-ads/api/docs/oauth/multi-party-approvals) (2026-10-14) | platform feature | block access changes | a second admin approves user invites, role changes and removals, MCC linking of existing accounts and billing changes; "only applicable for accounts with more than 3 administrators"; "API users are exempt" (contradicted by the API guide); manager-account 2-step-verification mandate for all sub-accounts (UI) | free substitute | direct substitute (Google) | all | no launch date; the page contradicts itself on emails |

## Offers, observed advertising and buyer spending

| Who | Kind | Promise | Price, unit, commitment | Job fit | Source, date |
|---|---|---|---|---|---|
| hacked.com | seller, and verified advertiser (Google, US, last shown 2026-10-21) | "Recover Your Meta Account - We can recover your business" | $149 call (sale; $249); $990 per accepted business case (sale; $1,499); $899/year optional support | adjacent (recovery) | #12, #13 |
| Nils Rooijmans (Gumroad) | seller | "Be in the know when someone, or something makes changes" in your Google Ads accounts | €170 one-time, per script | direct, partial (Google edits, MCC) | #14, 2026-10-22 |
| The Ad Spend | seller | change history "with the before and the after", threshold alerts | Starter free (no agency management); All Access $1,000/month at $10K of spend, scaling with spend | adjacent (Google and Meta changes; not framed as security) | #15, 2026-10-22 |
| nilsrooijmans.com, Clicktrain | free workaround | Google Ads scripts emailing on edits by users not on an approved list (the Clicktrain fork works at manager level and stops at 50 accounts) | free | direct, partial (Google) | intake; [Clicktrain](https://pages-clicktrain.nuxt.dev/blog/change-history-mcc-script-for-agency-directors/), via search |
| Meta, Google | free platform features | Security Center checklist; multi-party approval; 2-step-verification mandate | free | direct substitute, partial | #18, #19 |
| bfj.digital, saashero.net | sellers (agencies to advertisers) | "daily monitoring", security reviews, recovery help | quote ("Contact us now"), no price | adjacent (advertiser buyer) | intake; `pricing_scan_20261022-115631.json` |
| Spilno agency | seller (free) | Meta ads audit including account security | free, lead generation | adjacent | #17 |
| A client in Lahore | buyer spending | recover and lock down a hacked Business Manager | $10–30 budget; bids average $82 | adjacent | #16 |
| Meta Verified (consumer) | platform, buyer spending | live-agent support for locked accounts | $14.99/month (KGO-TV, Nov 2024) | adjacent (consumer recovery) | [abc7ny](https://abc7ny.com/post/paying-meta-verified-facebook-customer-service-cant-restore-stolen/15569756/), via search |

Pending tool rows (SearchAPI's monthly quota is used up: HTTP 429 on 2026-10-22):

- `pending: SearchAPI quota — rerun: uv run factory serp_ads --idea ad-account-watchdog --gl us --hl en --keywords "ad account security monitoring" "facebook business manager security audit" "google ads account hijacked" "facebook ad account hacked recovery service" "google ads mcc hijack" "protect client ad accounts from hackers" "meta ad account hacked agency" "google ads unauthorized user access alert"`
- `pending: SearchAPI quota — rerun: uv run factory ad_library --idea ad-account-watchdog --engine meta --q "ad account hacked" --country US`
- `pending: SearchAPI quota — rerun: uv run factory ad_library --idea ad-account-watchdog --engine linkedin --q "ad account security" --country US`
- `pending: SearchAPI quota — rerun: uv run factory ad_library --idea ad-account-watchdog --engine google_transparency --domain theadspend.com --region US`

The ads inspected by hand are the two hacked.com rows above.

## Route to buyers

| Channel | Reachable buyers or live opportunities | Rules | Founder work | Why this buyer would engage |
|---|---|---|---|---|
| reddit_reply | 4 agency-side posters in r/FacebookAds, 2026-09-30 to 2026-10-05 (#1–#4); threads open (Reddit archives after 6 months) | r/FacebookAds snapshot (Arctic Shift, retrieved by the archive 2025-01-21): "just posting a link to your service IS ABSOLUTELY NOT ALLOWED", "SOME promotional content" allowed when it brings "a TON OF VALUE"; no rule on DMs. The live page was not reachable | about 15 min per useful reply, plus about 15 min a week for the archive sweep (41–232 s of throttle per run) | mid-incident or just after: a lockdown checklist and a "who holds the keys" check answer their question |
| reddit_post / community_post | r/FacebookAds (value post with moderator approval); r/PPC and r/agency ban service threads | r/PPC: "posting a thread of services or tools by agencies" is spam; r/agency: "No Unsolicited DMs … grounds for immediate banning" | about 2 h for a value post | the October wave (#1–#4), the MCC hijacks (#6) |
| linkedin_outreach | burned: 2 agency founders under #MCCGoogleAdsHijack, Dec 2025 – Feb 2026 (#6 and a commenting agency CEO). Untriggered: one web search listed 5 UK agency founders who fit (WeDiscover, Adbetter, Pixated, PPC Geeks, Touchpoint) | free accounts reportedly 3–5 personalized notes a month and 80–100 invitations a week (third-party estimates, [expandi](https://expandi.io/blog/linkedin-connection-message-templates/), [linkedfusion](https://linkedfusion.io/blogs/linkedin-limits-guide/)); LinkedIn's own page not read | about 10 min per researched message | the trigger exists for the burned only; for the rest it is prevention with no trigger |

R = 1:
- Three current target buyers (#1–#3, plus #4) are reachable by reply. The rules were checked from
  the archive snapshot.
- A repeatable next batch is not shown: about one agency-side thread a week at best, so the next
  three take three weeks or more.

## Promise verification

Google pages are dated 2026-10-13 to 2026-10-21; Meta pages show no date. The subagent's full table,
with verbatim quotes, is in the collapsed block after the limits. Re-checked by hand on 2026-10-22: the Meta activity
event types and Google's multi-party approval page.

| Platform | Claim | Documented capability | Permission needed | Latency | Status | Source |
|---|---|---|---|---|---|---|
| Google Ads | alert on a new user or role change | users and pending invitations are readable as state; changes pending a multi-party approval do not show in Search | ADMIN access on the target account; Basic access level (Explorer blocks user management) | polling; no event | partial | [managing users](https://developers.google.com/google-ads/api/docs/account-management/managing-users) (2026-10-14) |
| Google Ads | alert on a new manager link | link status (PENDING, ACTIVE…) readable on CustomerManagerLink / CustomerClientLink | manager or client authentication | polling; links are not change events | partial | [linking](https://developers.google.com/google-ads/api/docs/account-management/linking-manager-accounts) (2026-10-15) |
| Google Ads | alert on a budget jump | ChangeEvent covers CAMPAIGN_BUDGET, with who made the change; "up to three minutes" late; 30 days; "not all changes" recorded | developer token | about 3 min plus the poll | supported (campaign budgets); account budget: state only | [change event](https://developers.google.com/google-ads/api/docs/change-event) (2026-10-14) |
| Google Ads | alert on a new payment method | billing setup and payments account readable, scoped to monthly invoicing; the card or bank is not exposed | Basic (Explorer blocks billing) | polling | partial (a billing-setup diff, not a card) | [billing](https://developers.google.com/google-ads/api/docs/billing/overview) (2026-10-14) |
| Google Ads | "within minutes" across 50 accounts | Explorer 2,880 operations/day; Basic 15,000 (brand verification first, no stated delay); Standard unlimited ("10 business days") | developer token from an MCC | at about 6 queries per account per round: one round every ~29 min at 50 accounts on Basic, every ~6 min at 10 (arithmetic) | partial | [access levels](https://developers.google.com/google-ads/api/docs/api-policy/access-levels) (2026-10-19) |
| Google Ads | apply security settings | no API found to set 2-step verification or multi-party approval: settings in the interface; Google already offers a manager-account 2-step-verification mandate for all sub-accounts | — | — | unsupported by API (undocumented); a checklist | #19; [2SV](https://support.google.com/google-ads/answer/12864186) |
| Meta | alert on a new person or system user in the portfolio | `business_users`, `system_users`, `pending_users` edges, read as state | `business_management`, Advanced (Full) access through App Review and Business Verification | polling; no Business webhook | partial | [Business reference](https://developers.facebook.com/docs/marketing-api/reference/business/) |
| Meta | alert on a new partner or agency | `/{business}/agencies`, `/act_{id}/agencies` with access_requested_time and access_updated_time | as above | polling | partial | [ad account agencies](https://developers.facebook.com/docs/marketing-api/reference/ad-account/agencies/) |
| Meta | alert on a user added to an ad account | `/act_{id}/activities` logs `ad_account_add_user_to_role` and `ad_account_remove_user_from_role` | `ads_read` (Advanced for other businesses' accounts) | polling; one week by default; retention and delay undocumented | partial | [ad activity](https://developers.facebook.com/docs/marketing-api/reference/ad-activity/) (checked by hand) |
| Meta | alert on a new funding source | `add_funding_source`, `remove_funding_source` events; `funding_source_details` needs the MANAGE task on each account; #1's agency had no billing access to its clients' accounts | MANAGE task per ad account | polling; delay undocumented | partial | [ad account](https://developers.facebook.com/docs/marketing-api/reference/ad-account/) |
| Meta | alert on a budget or spend-limit jump | `update_campaign_budget`, `update_ad_set_budget`, `ad_account_update_spend_limit`; spend_cap and amount_spent fields | `ads_read` | polling; delay undocumented | partial | [ad activity](https://developers.facebook.com/docs/marketing-api/reference/ad-activity/) |
| Meta | push alerts | webhook objects include no Business; the Ad Account fields cover none of these changes | — | — | unsupported | [webhooks](https://developers.facebook.com/docs/graph-api/webhooks/reference/) |
| Meta | apply the 2FA requirement | the Business field `two_factor_type` (none, admin_required, all_required) is documented as writable; a write ends "read-only" | business admin (unknown, measure on a sandbox) | — | partial (documented, untested) | [Business reference](https://developers.facebook.com/docs/marketing-api/reference/business/) |
| Meta | a live automated test this week | Limited access is "For development only. Not for production apps running for live advertisers"; Advanced needs App Review and Business Verification, no stated review time | — | — | blocker for live client accounts this week | [authorization](https://developers.facebook.com/docs/marketing-api/overview/authorization) |
| Others ("etc.") | TikTok, LinkedIn, Microsoft | not reached | — | — | undocumented (not reached) | — |

Limits for the challenge:
- The honest promise is "detected at the next poll", not "within minutes": about 3 minutes for
  Google budgets, a quota-bound interval for Google access, an undocumented delay on Meta.
- "Read-only" needs admin-grade keys: ADMIN on Google user access, MANAGE on Meta funding. The
  watchdog becomes a key holder its own audit must list.
- "Apply all sec settings" is one documented write on Meta and a checklist on Google.
- Meta's live client accounts are out of reach until App Review passes.
- A login hijacked with no new user (#4, #5) is caught only by a campaign or spend alert.

<details><summary>Platform documentation, verbatim quotes (subagent, 2026-10-22; Meta quotes via the
fetch tool's extraction)</summary>

| Platform | Claim id and claim | Documented capability (verbatim quote) | Permission needed | Latency (event lag or polling) | Status | Source URL, page date |
|---|---|---|---|---|---|---|
| Google Ads API | **G1** List users with their access role (CustomerUserAccess) and pending invitations (CustomerUserAccessInvitation) | "You can get the list of users with access to an account by building a Google Ads Query Language statement to query all the CustomerUserAccess entities associated with a customer ID." / "Querying customer_user_access returns only confirmed users. Pending invitations can be queried using customer_user_access_invitation." / "If a user access level change is pending a multi-party approval, then it won't show up when retrieving user access lists using the GoogleAdsService.Search or GoogleAdsService.SearchStream method." | "To manage user access, the calling user or service account must have ADMIN access to the target account." Invitations: "Calling these APIs requires an authenticated user with ADMIN access privileges on the target customer account." Explorer level restricts "User management" (CustomerUserAccessService, CustomerUserAccessInvitationService): Basic or Standard needed. | Polling of state (GAQL Search), no event. "It can take up to 24 hours for the status to change from pending once the invitation is accepted." Changes waiting for MPA approval are invisible to Search. | supported (state, by polling; ADMIN-level caller) | https://developers.google.com/google-ads/api/docs/account-management/managing-users (Last updated 2026-10-14); https://developers.google.com/google-ads/api/docs/account-management/managing-invitations (2026-10-14); https://developers.google.com/google-ads/api/reference/rpc/v26/CustomerUserAccess (2026-10-13) |
| Google Ads API | **G2** Manager links: new link requests and active links (CustomerManagerLink, CustomerClientLink), their status | "Account linking must be initiated by the manager account and accepted by the client account. The state of the link is tracked in the status field of the CustomerClientLink or CustomerManagerLink resource." ManagerLinkStatus: "PENDING Indicates relationship has been requested by manager, but the client hasn't accepted yet." (also ACTIVE, INACTIVE, REFUSED, CANCELED). Help Center: "When a manager account (MCC) submits a request to link an existing, independent Google Ads account as a child account, Multi-party approval (MPA) is enforced to safeguard both accounts." | Not stated for reads. The linking steps authenticate as the manager (invite) or the client (accept). | Polling of state. Links are not a ChangeEvent resource type (G3). The guide's query looks up a single link by resource name and shows no query that lists every pending link. | supported (state, by polling) | https://developers.google.com/google-ads/api/docs/account-management/linking-manager-accounts (2026-10-15); https://developers.google.com/google-ads/api/reference/rpc/v26/ManagerLinkStatusEnum.ManagerLinkStatus (2026-10-13); https://support.google.com/google-ads/answer/16891189 (no date shown) |
| Google Ads API | **G3** ChangeEvent: which change_resource_type values, delay, lookback, row limit; ChangeStatus | Full enum: "AD, AD_GROUP, AD_GROUP_AD, AD_GROUP_ASSET, AD_GROUP_BID_MODIFIER, AD_GROUP_CRITERION, AD_GROUP_FEED, ASSET, ASSET_SET, ASSET_SET_ASSET, CAMPAIGN, CAMPAIGN_ASSET, CAMPAIGN_ASSET_SET, CAMPAIGN_BUDGET, CAMPAIGN_CRITERION, CAMPAIGN_FEED, CUSTOMER_ASSET, FEED, FEED_ITEM" (+ UNKNOWN, UNSPECIFIED). There is no type for user access, invitations, manager links, billing setup, account budget or the customer itself. "A change can take up to three minutes to be reflected in the change event results." / "Queries for Change Event data must filter by date within the past 30 days and be limited to a maximum of 10,000 rows." / "not all changes to your account will have a corresponding change event entry." / "Fetching Google Ads Editor changes using the change_event report is not supported". ChangeStatus: "The query must filter on a date within the past 90 days"; "Change status is not tracked for a specific resource's changed values—only which resources have changed." Its type list is also campaign-side only. | Not stated on the page. ChangeEvent is not in Explorer's restricted list. | Polling a change log. Lag "up to three minutes"; 30-day lookback (ChangeStatus: 90 days); 10,000 rows per query; not every change is recorded. | supported for campaign-side entities. unsupported for users, manager links and billing: they are absent from the closed enum. | https://developers.google.com/google-ads/api/docs/change-event (2026-10-14); https://developers.google.com/google-ads/api/reference/rpc/v26/ChangeEventResourceTypeEnum.ChangeEventResourceType (2026-10-13); https://developers.google.com/google-ads/api/docs/change-status (2026-10-21) |
| Google Ads API | **G4** Payment method and billing (BillingSetup, PaymentsAccount, AccountBudget): can a new payment method be detected? | "The payments setting in your Google Ads account must be configured for monthly invoicing in order to manage billing setups, account budgets, and invoices with the Google Ads API." BillingSetup is read with GAQL "FROM billing_setup" (payments_account_id, payments_profile_id, status PENDING / APPROVED_HELD / APPROVED / CANCELLED). PaymentsAccount fields are only currency_code, name, paying_manager_customer, payments_account_id, payments_profile_id and secondary_payments_profile_id. No card or bank field is exposed. AccountBudget: "Any new account budgets pending approval, along with any existing account budgets that have updates pending, will also populate the pending_proposal nested message". | Explorer restricts "Account Billing and Payment" (PaymentsAccountService, BillingSetupService, AccountBudgetProposalService, InvoiceService): Basic or Standard needed. | Polling of state only. These resources are not ChangeEvent types. | partial: billing setup, payments account and account budget are readable, and the overview scopes billing to monthly invoicing. The payment instrument itself is undocumented. "New payment method" can only mean a billing_setup diff found by polling. | https://developers.google.com/google-ads/api/docs/billing/overview (2026-10-14); https://developers.google.com/google-ads/api/docs/billing/billing-setups (2026-10-14); https://developers.google.com/google-ads/api/reference/rpc/v26/PaymentsAccount (2026-10-13); https://developers.google.com/google-ads/api/docs/billing/account-budgets (2026-10-14) |
| Google Ads API | **G5** Budget changes (CampaignBudget amount) via ChangeEvent | "CAMPAIGN_BUDGET A CampaignBudget resource change." / "You can retrieve data such as specific field values that have changed, who made the change, and which client type was used to make the change." The account-level spending limit (AccountBudget) is not in the enum. It is read as state (approved_spending_limit_micros, pending_proposal). | As G3 | Polling change_event: lag "up to three minutes", 30-day window, and "not all changes" are recorded. | supported for campaign budgets. Account-level budget: state polling only. | https://developers.google.com/google-ads/api/docs/change-event (2026-10-14); https://developers.google.com/google-ads/api/reference/rpc/v26/ChangeEventResourceTypeEnum.ChangeEventResourceType (2026-10-13) |
| Google Ads API | **G6** API access: developer token levels, daily limits, third-party reads through the OAuth of an MCC user, review time | Explorer "2,880 operations / day for production accounts" ("automated review and approval in most cases"). Basic "15,000 operations / day for both test and production accounts". Standard "Unlimited operations / day for both test and production accounts", review "10 business days". "API operations are the total sum of Search and SearchStream requests, individual mutate operations, and other service requests." "Completing brand verification for your Google Cloud project is a prerequisite to apply for Basic access level." "Google may automatically upgrade your project's API access level to Basic once you submit your application." Third party: "My app will build a user screen that lets the signed-in users connect to their Google Ads accounts and authorize my app to manage those accounts on their behalf. Use multi-user authentication." "If your access to the customer account is through a manager account, this header is required and must be set to the customer ID of the manager account." | Developer token: "Applying for a developer token involves selecting or creating a Google Ads manager account and then completing the API Access form in the API Center." The app also needs OAuth consent from a user with access to the agency MCC. | Not applicable. Quotas count over a sliding 24-hour period ("'Per day' is based on a sliding 24 hour time period"). | supported. Basic review time: undocumented (no duration given). Standard: "10 business days". Known issue: "some users with brand verified projects are rejected when applying for Basic access." | https://developers.google.com/google-ads/api/docs/api-policy/access-levels (2026-10-19); https://developers.google.com/google-ads/api/docs/best-practices/quotas (2026-10-14); https://developers.google.com/google-ads/api/docs/oauth/overview (2026-10-14); https://developers.google.com/google-ads/api/docs/concepts/call-structure (2026-10-14); https://developers.google.com/google-ads/api/docs/api-policy/developer-token (2026-10-19) |
| Google Ads API + Help Center | **G7** Security settings via API: 2-Step Verification enforcement, multi-party approval (what it covers, launch date) | API guide: "The Google Ads API supports multi-party approvals for three actions: Inviting a new user to an account / Changing the user access level of an existing user / Removing an existing user from the account". Pending requests are readable with "FROM multi_party_auth_review WHERE multi_party_auth_review.review_status = PENDING" and resolved with "MultiPartyAuthReviewService.ResolveMultiPartyAuthReview". Help page: "Note : Read-only roles and API users are exempt from this approval process." (this contradicts the API guide, which says the API "may generate a multi-party approval request"). "Multi-party approval is only applicable for accounts with more than 3 administrators." 2SV is a UI path in every page read: "Under the "Verification during sign-in" section, select the 2-Step Verification drop down. Select Turn on." Manager mandate (UI): "admin users of manager accounts can require that users of owned sub-accounts enable 2-Step Verification or Advanced Protection on their accounts to login." The only per-user signal in the API: "passkey_enabled ... Output only. Whether the user has passkey enabled." | Resolving an MPA request needs "the credentials of the user who is authorized to resolve the request. This is typically a second administrator of the account." | MPA requests: polling multi_party_auth_review (requests expire after 20 days). | partial: reading MPA requests and the passkey flag is supported. Setting or enforcing 2SV, or turning MPA on, through the API: undocumented (no field or method found; UI paths only). MPA launch date: undocumented (neither the help page nor the API guide shows one). | https://developers.google.com/google-ads/api/docs/oauth/multi-party-approvals (2026-10-14); https://support.google.com/google-ads/answer/16891189 (no date shown); https://support.google.com/google-ads/answer/12864186 (no date shown); https://support.google.com/google-ads/answer/12865295 (no date shown); https://developers.google.com/google-ads/api/reference/rpc/v26/CustomerUserAccess (2026-10-13) |
| Google Ads Help Center | **G8** Google's own notifications when a user is added or access changes | "Google Ads sends automated email notifications for Multi-party approval (MPA) requests." Approval Request goes to "All eligible Google Ads Account Administrators in the hierarchy." Pending Reminder: "Send one reminder email if the MPA is not approved after 3 days." The same page also says "Since emails aren't sent for these approvals, it's important to check your in-product notifications regularly." and "email reminders are sent every 6 hours". The Security requests tab groups requests "by category (such as User Management, MCC Account Linking, or Billing changes)". Mandates: "admin users of owned sub-accounts will receive an email and will notice a banner notification in Google Ads that informs them of the change." | Recipients are account admins. | Native push (in-product, and email per part of the page) for MPA-gated actions. | partial: MPA-gated actions only, and the page contradicts itself on email. A plain "user added" notification without MPA: undocumented. | https://support.google.com/google-ads/answer/16891189 (no date shown); https://support.google.com/google-ads/answer/12865295 (no date shown) |
| Meta (Graph / Business Management API) | **M1** People in a business portfolio with their roles; system users; pending users | Business node edges: "business_users": "Business users associated with this business. Includes employees and admins at the business."; "system_users": "The business's system users."; "pending_users": "Admin for this business invited this user to the business. Pending user approval." | Not named on the reference page. business_management: "allows your app to read and write with the Business Manager API." Limited tier: "No Business Manager access to manage ad accounts, user permissions, and Pages." | Polling of state. There is no Business webhook (M6). | partial: the edges are documented, but the role field and its values were not read (the business_users edge page body did not render for the fetcher). | https://developers.facebook.com/docs/marketing-api/reference/business/ (no date shown); https://developers.facebook.com/docs/marketing-api/reference/business/business_users/ (body not rendered) |
| Meta | **M2** Partners and agencies with access (/{business-id}/agencies, /clients, /act_{id}/agencies, /act_{id}/assigned_users) | Business node: "agencies": "Agencies associated with this business."; "clients": "Clients of this business."; "pending_client_ad_accounts": "This business requested access to these client ad accounts and is pending approval." /act_{id}/agencies: "Agencies associated with ad accounts.", with "access_status" ("The status of the access request"), "permitted_tasks", "access_requested_time" and "access_updated_time". /act_{id}/assigned_users: "Business and system users assigned to this Ad Account."; "tasks": "All unpacked roles/tasks of this particular user on this object"; the "business" parameter is required. | Not named on these pages (error 200 "Permissions error"). | Polling of state. access_requested_time and access_updated_time make diffs possible. | supported (state, by polling). The access_status values are not listed. | https://developers.facebook.com/docs/marketing-api/reference/business/ ; https://developers.facebook.com/docs/marketing-api/reference/ad-account/agencies/ ; https://developers.facebook.com/docs/marketing-api/reference/ad-account/assigned_users/ (no dates shown) |
| Meta | **M3** /act_{id}/activities: event_type values, retention, latency | Edge: "The activities of this ad account" (Edge<AdActivity>). The 100 event_type values include "ad_account_add_user_to_role", "ad_account_remove_user_from_role", "add_funding_source", "remove_funding_source", "ad_account_update_spend_limit", "ad_account_reset_spend_limit", "ad_account_remove_spend_limit", "update_campaign_budget", "update_ad_set_budget", "update_campaign_group_spend_cap", "billing_event" and "funding_event_successful". Fields: "actor_id", "actor_name", "extra_data" ("JSON encoded extra information"). The edge page says: "This endpoint doesn't have any parameters". | Not named on the pages. | Polling a per-ad-account log. Retention: undocumented. Latency: undocumented. No event_type covers a partner or agency gaining access, and none covers business-portfolio people. | partial | https://developers.facebook.com/docs/marketing-api/reference/ad-activity/ ; https://developers.facebook.com/docs/marketing-api/reference/ad-account/activities/ ; https://developers.facebook.com/docs/marketing-api/reference/ad-account/ (no dates shown) |
| Meta | **M4** Funding source details on the ad account | "funding_source": "ID of the payment method."; "funding_source_details" (FundingSourceDetails): "To access this field, the user making the API call must have a MANAGE task permission for that specific ad account." | MANAGE task on each ad account | Polling of state. Changes are also logged as add_funding_source / remove_funding_source (M3). | supported (state, by polling, at MANAGE level) | https://developers.facebook.com/docs/marketing-api/reference/ad-account/ (no date shown) |
| Meta | **M5** spend_cap, amount_spent, campaign daily_budget / lifetime_budget | "spend_cap": "The maximum amount that can be spent by this Ad Account. When the amount is reached, all delivery stops."; "amount_spent": "Current amount spent by the account with respect to spend_cap. Or total amount in the absence of spend_cap." The campaign reference page was not read. Changes are logged as "update_campaign_budget" / "update_ad_set_budget" (M3). | ads_read / ads_management (permissions page; the field rows name no permission) | Polling of state, plus the activities log for changes. | supported for spend_cap and amount_spent. Campaign budget fields: undocumented (not reached). | https://developers.facebook.com/docs/marketing-api/reference/ad-account/ (no date shown); https://developers.facebook.com/docs/marketing-api/reference/ad-activity/ |
| Meta | **M6** Webhooks pushing changes to business users, roles, partners, funding sources or ad account settings | Webhook objects: "Ad Account", "Application", "Catalog", "Instagram", "Managed Meta Account", "Page", "Permissions", "User", "Whatsapp Business Account". There is no Business object. Ad Account fields: "ads_async_creation_request", "creative_fatigue", "ad_recommendations", "in_process_ad_objects", "product_set_issue", "with_issues_ad_objects". | Not applicable | No push for these changes: polling only. | unsupported (absent from the documented lists of objects and fields) | https://developers.facebook.com/docs/graph-api/webhooks/reference/ ; https://developers.facebook.com/docs/graph-api/webhooks/reference/ad-account/ (no dates shown; v26.0) |
| Meta | **M7** Permissions, access tiers, App Review, Business Verification, review time, rate limits | ads_read: "for Ad accounts you own or have been granted access to by the owner or owners of other ad accounts". business_management: "allows your app to read and write with the Business Manager API". App Review asks: "Provide specific examples of why your app requires managing business assets on behalf of other businesses." Business Verification "is required for all apps making requests for Advanced Access." Tiers were renamed: "Standard Access" became "Limited Access" and "Advanced Access" became "Full Access". Limited: "Heavily rate-limited per ad account. For development only. Not for production apps running for live advertisers." Full requires "at least 500 Marketing API calls in the last 15 days" and "an error rate of less than 15% in the last 500 calls". Other businesses' accounts: "you need advanced access to the ads_read and/or ads_management permissions." BUC: "Calls within one hour = 300 + 40 * Number of Active ads" (standard) vs "100000 + 40 * Number of Active Ads" (advanced). BUC types: "ads_insights, ads_management, custom_audience, instagram, leadgen, messenger, or pages". | Advanced access to ads_read, plus business_management for people and partners, through App Review and Business Verification | Rolling one-hour BUC window | supported (the path is documented). Review time: undocumented (the page says only that "Meta responds with an approval or denial"). | https://developers.facebook.com/docs/permissions/ ; https://developers.facebook.com/docs/marketing-api/overview/authorization ; https://developers.facebook.com/docs/graph-api/overview/rate-limiting/ (no dates shown; the en_US locale was used for quotes) |
| Meta | **M8** Security settings via API: Business two_factor_type (read / write), API to enforce 2FA; Security Center | Business field "two_factor_type": "The two factor type authentication used for this business." Update parameter on POST /{business_id}: "two_factor_type enum{none, admin_required, all_required}", described as "Two-factor type of the business". No other security setting was found. The Security Center help page body did not render for the fetcher. | Not named on the page. A write presumably needs a business admin token with business_management: unknown, measure with a sandbox call. | Not applicable for a setting; the current value is read by polling. | two_factor_type read and write: supported per the reference, not tested. Security Center: undocumented (not read). | https://developers.facebook.com/docs/marketing-api/reference/business/ (no date shown); https://www.facebook.com/business/help/216940652189296 and https://www.facebook.com/business/help/280940009201586 (bodies not rendered) |
| Meta | **M9** Meta's own notifications when a person or partner is added | Not reached | Not reached | Not reached | undocumented (not reached) | Not reached |
| LinkedIn / Microsoft Advertising / TikTok | Optional: adAccountUsers; user roles API; Business Center members API | Not reached | Not reached | Not reached | undocumented (not reached) | Not reached |

</details>

## Complaints and incidents

28 incidents after deduplication (46 hits in 41 threads), across two sweeps:

| Sweep | Window | Venues | Screened → takeover incidents | Notes |
|---|---|---|---|---|
| intake, "ad account hacked" | 2026-07-24 to 2026-10-22 | r/FacebookAds, r/PPC, r/googleads | 22 hits (16 posts, 6 comments) → 15 | 1 lockout, 1 roundup and 4 off-topic comments set aside |
| triage, "business manager hacked" | 2025-10-22 to 2026-10-22 | r/FacebookAds hits only; the other subreddits were skipped by the throttle | 24 posts → 4 duplicates of the intake, 13 new incidents | 5 off-topic and 2 unclear set aside |

- Completeness: lower bounds (`complete: false` on both). The deduplication rule is one incident
  per thread.
- 8 incidents were more than a year old when posted.
- 27 of the 28 incidents are Meta and 1 is Google; Google incidents surface on LinkedIn and in the
  trade press instead (#6, #7).
- Agency or freelancer side: 7. They are #1–#5, a freelancer's older $10K hack (thread 1w6kkv0) and
  an agency employee's two-year-old hack (1rq5cg8). An operator with 8 Business Managers and 12 ad
  accounts (1tkxvao) did not state a role.

| Date | Role | Platform | Stage | Action taken | Loss (reported: gross / refund / net) | Link |
|---|---|---|---|---|---|---|
| 2026-10-05 | agency | Meta | detected early | removed a planted system user, killed campaigns | $20,000/day budgets set / unknown / unknown | #1 |
| 2026-10-02 | portfolio manager | Meta | after, recovery | refund case since June | $10,061.30 / "processed", not received / unknown | #2 |
| 2026-09-30 | agency | Meta | after | asks for recovery and an audit trail | best ads deleted / — / — | #3 |
| 2026-10-03 | consultant | Meta | during | 2FA loop, client removing the staff member | unknown | #4 |
| 2026-10-13 | unknown | Meta | after | asks for a specialist (post removed) | ~$5,000 / unknown / unknown | [1x4q1wl](https://www.reddit.com/r/FacebookAds/comments/1x4q1wl/meta_business_manager_hacked_5000_unauthorized_ad/) |
| 2026-10-21 | small-business owner | Meta | after | refund request, PayPal dispute denied | $1,129.89 / denied / $1,129.89 | intake |
| 2026-07-30 | freelancer | Google | after | appeal of a cloaking suspension | "Almost $500" / unknown / unknown | #5 |
| 2026-05-22 | operator of 8 Business Managers and 12 ad accounts | Meta | after | case under review, no original admin left | unknown | [1tkxvao](https://www.reddit.com/r/FacebookAds/comments/1tkxvao/meta_business_manager_multiple_ad_accounts_hacked/) |
| 2025-11-15 | agency founder | Google MCC | after | over two dozen tickets, public escalation | not stated | #6 |
| 2025-12-13 | advertiser (NL) | Google, via an agency's MCC | after | blocked payment methods, traced the breach | "over €40,000" claimed | #7 |

Quotes that carry a decision:

- "not adding another user to the account" (#4): the framing. A new-user alert misses this case.
- "The original MCC owner was removed" (#6): the Google side. The manager link is the asset to
  watch.

## Demand (search)

`keyword_volume` was not run:
- Search is not an eligible channel: `google_search` is locked because `assets.google_ads` is not
  set.
- SearchAPI's quota is used up.

If search becomes a channel, rerun with buckets built from the buyers' own language:
`uv run factory keyword_volume --idea ad-account-watchdog --cc us --buckets-file ideas/ad-account-watchdog/research/buckets.json --language en`.

## Landscape

- **Incumbents:**
  - Recovery sellers advertise and price per case (hacked.com, #12, #13).
  - Change-history tools sell edit alerts, framed as control, not security: €170 one-time for a
    Google MCC script (#14); agency change history inside a $1,000/month plan (#15).
  - Agencies sell "daily monitoring" and security reviews to advertisers on quote (intake: bfj.digital,
    saashero.net).
  - No product for ad-account takeover monitoring aimed at agencies was found.
  - Not found in this sweep: a tool that alerts when a person, system user or partner is added to
    a Meta Business Manager. Queries: "tool notify when new admin or system user added to Meta
    Business Manager", "Google Ads MCC security monitoring software agencies", "ad account
    takeover monitoring tool for agencies". Web search, 2026-10-22.
- **Free substitutes:**
  - Google Ads scripts for change history (Google only, edits only, hours of lag, up to 50
    accounts).
  - Meta's and Google's own security features: Security Center, multi-party approval, the
    2-step-verification mandate.
  - Spending limits set by hand. The top advice in #1's thread, but #1's agency could not reach
    billing settings.
- **Platform and institutional:**
  - Google's multi-party approval covers access, MCC-linking and billing changes, only for accounts
    with more than 3 administrators (#19).
  - Trade press: the MCC hijack wave of late 2025 (Search Engine Land, in the intake); Google's
    warning emails and passkeys in 2026 ([almcorp](https://almcorp.com/?p=74426), via search); a
    stolen-account resale market ([PropellerAds on Malwarebytes](https://propellerads.com/blog/adv-ad-account-hijacking/),
    via search).
  - Strongest counter-evidence to the proposed framing: #4 and #5, with no new user and 2FA in
    place, and Google's free multi-party approval for the access changes the watchdog would alert
    on.

## AdsInsights

Not run: no named question it would settle. No category plausibly matches ad-account takeover
protection for agencies; the nearest are "cybersecurity" or "marketing software", which the triage
rejects as generic.

## Economics

| Scenario | Value per customer | Assumptions (from `value_basis`) | Allowed CAC (value / 3) |
|---|---|---|---|
| low | 319 EUR | 59 EUR/month (Vlad's call) × 6 paying months (default, unknown) × 0.9 margin (default); no audit | 106 EUR |
| base | 418 EUR | low + 599 EUR audit (Vlad's call) × 0.33 attach rate (bet) × 0.5 margin (bet) = 99 | 139 EUR |
| high | 432 EUR | 4 EUR per account × 20 accounts (bet) × 6 × 0.9; no audit | 144 EUR |

Founder time at 100 EUR/h counts in the cost per primary event:
- a useful Reddit reply (about 15 min) is 25 EUR;
- a 20-minute conversation is 33 EUR;
- a manual audit (3 h, the intake's bet) is 300 EUR.

At the base value, four 20-minute conversations (133 EUR) use up the allowed CAC of 139 EUR,
before any reply time is counted.

Primary-event-to-customer conversion: `unknown — measure by the prepared test` (replies → conversations →
a paid month or a paid audit, counted per owner).

## Signals

| Signal | Score | Evidence (record numbers) |
|---|---|---|
| P buyer problem and action | 2 | two independent agency-side incidents with actions in the last 30 days: #1 (caught it, removed the planted user) and #2 (a refund case since June); also #3 and #6. The actions are recovery, not prevention, and the owners' roles are unverified |
| C commercial evidence | 1 | #14: a current, priced offer (€170 one-time) for MCC holders to be alerted when someone changes their Google Ads accounts. Partial (Google edits only), framed as change control. The recovery offers and ads (#12, #13) and buyer spending (#16) are adjacent and do not count. No firsthand evidence of an agency paying for prevention |
| R unpaid reachability | 1 | four current agency-side posters reachable by reply (#1–#4), rules checked from the archive's snapshot. No repeatable weekly batch (about one thread a week); LinkedIn rules not checked by the source |

## Gate

**PASS**: R ≥ 1 and P = 2. P ≥ 1 and C ≥ 1 also hold, from independent sources: Reddit and
LinkedIn for P, Gumroad for C.

Minimum coverage is met:
- Two independent venues where this buyer appears: r/FacebookAds with r/PPC, and LinkedIn.
- One search for offers, spending and free substitutes.
- A second eligible channel checked: LinkedIn.

PASS authorizes the challenge, not a launch.

## Open questions for the challenge

- **Prevention or recovery?**
  - For: #1 values speed ("caught it quickly"); #3 asks for the change log.
  - Against: every sale and ad seen is recovery (#12, #13); the observed spending is a refund chase
    (#2) and a $10–30 budget (#16).
  - Alternatives: the watchdog at 59/month; a paid one-shot lockdown audit; a rapid-response
    retainer for agencies.
  - The finding that would change the decision: among ten burned agency owners shown a real audit,
    how many pay month one against how many buy the audit once or ask for recovery help.
- **Can Meta be in the test this week?**
  - For: the activity log records user-role, funding-source, spend-limit and budget events; people
    and partners are readable.
  - Against: Advanced access needs App Review and Business Verification, with no stated delay; no
    webhooks; Meta's delay is undocumented.
  - Alternatives: a concierge audit run on the agency's own login during a call; Google automated
    and Meta manual.
  - The finding that would change the decision: a Limited-access probe on a personal Business
    Portfolio showing the activities log's lag, and whether a test agency can add the app as a
    developer.
- **Will an agency hand admin-grade keys to a watchdog?**
  - For: #9 shows clients moving accounts to an agency for safety, so trust is transferable.
  - Against: the watchdog becomes a new key holder; #7's breach came through a third party's
    standing access.
  - Alternatives: a script the agency runs in its own MCC (as #14 does); an export-and-diff audit
    with no stored token.
  - The finding that would change the decision: three of five owners agree to connect ADMIN/MANAGE
    access in the conversation.
- **Who is the buyer: the agency owner, the freelancer or the advertiser?**
  - For the agency: #1, #2, #3, #6.
  - For the others: #4, #5 (freelancers) and #7 (the advertiser bears the agency's drift).
  - Alternatives: agency owners holding 10–50 accounts; freelancers at a lower price; advertisers
    auditing their agencies.
  - The finding that would change the decision: who answers the first ten replies, and who says
    they would pay.
- **Which price anchor wins?**
  - For a higher price: incidents of $10K+ (#1, #2, #7); recovery cases at $990 (#12).
  - For a lower one: a €170 one-time script (#14), free change history (#15), a free audit (#17).
  - Alternatives: 599 + 59; 149 one-shot; 59 alone.
  - The finding that would change the decision: the price at which burned owners say yes in the
    ten conversations.

## Carried forward

- **Queries not run:**
  - "MCC hacked" (r/PPC, r/googleads, r/agency), and "business manager hacked" outside
    r/FacebookAds: skipped by the archive's throttle.
  - "unauthorized charges" and "hacked ad account" (from the intake).
  - Facebook groups and Slack communities of agency owners; X.
  - Meta's own notifications when a person or partner is added; the other networks' APIs.
  - The live subreddit rules: Reddit is blocked for the session.
- **Pending tool rows:** `serp_ads` and three `ad_library` calls (commands under § Offers), after
  SearchAPI's monthly quota resets (date unknown: check the SearchAPI dashboard).
- **For the conversations of the prepared test, settle:**
  - whether the owner holds client accounts in the agency's own Business Manager or MCC, and how
    many;
  - whether they were burned, and how they found out (minutes or weeks);
  - what they paid afterwards (a recovery service, Meta Verified, refund work);
  - whether they would connect admin-level access;
  - whether they would buy the audit, the month or both.

## Cost and time

- Cash: 0.00 → 0.05 EUR, all `api` (5 Firecrawl pages for `pricing_scan`). `serp_ads` failed with
  HTTP 429 and logged nothing.
- The subagent's reading and the session's web search cost no cash.
- Wall-clock: 48 minutes, from 11:43:40 to 12:31. Research stopped at minute 41, the brief was
  written by minute 48.
- Cut or pending: the SERP and ad-library tools, the Meta Ad Library, the live Reddit rules, the
  other networks.
