# Intake — Ad Account Watchdog

## Pitch (verbatim)

> monitor proactively your ad network accounts - and apply all sec settings - against hackers taking over - on Google ads, Facebook ads etc.

Working title: Ad Account Watchdog. Slug: `ad-account-watchdog`. Intake on 2026-10-22, free tools only; the outside voice cost a few cents.

## Homework

Four bets before the evidence, rewritten with it (nothing spent):

- **Q1 Demand reality.** Bet: loud, recurring pain. Evidence: Reddit r/PPC + r/FacebookAds + r/googleads, 2026-07-24 to 2026-10-22, phrase "ad account hacked": 16 posts and 6 comments (FacebookAds 16, PPC 6), a lower bound (`complete: false`, the archive throttled; `research/reddit_mentions_20261022-095725.json`). "business manager hacked": 0 in a second, also incomplete pass on FacebookAds + PPC (`research/reddit_mentions_20261022-100611.json`); "unauthorized charges" and "hacked ad account" never got searched within the waiting budget. Hacker News, 2025-10-22 to 2026-10-22 (`research/hn_mentions_20261022-095311.json`, complete): "ad account hacked" 0 stories and 3 off-topic comments, "Google Ads account hacked" 1 story, "ad account hijacked" 1 story and 1 comment, both off-topic. Every Reddit post is post-breach: refunds, restrictions, 2FA loops. Nobody in the sweep pays for prevention. Position: recovery pain is proven, prevention demand is not; what would change it is one burned agency owner paying for the first month this week.
- **Q2 Status quo.** Bet: 2FA plus manual checks. Evidence: 2FA (often SMS), spend caps and card limits set once, quarterly access reviews and "daily monitoring" sold as a service by agencies (bfj.digital), a free Google Ads change-history alert script with up to a day of lag, Slack change alerts for Google only. Late discovery is common: "Two years ago my business portfolio got breached... discovered that 3 weeks ago"; "hacked in April... didn't realize this happened until now". Cost: the breach itself, $1,129.89 to $60,000 of fraudulent spend, 4 days locked out of an MCC, 4 months of case work for a $60k refund, accounts restricted 2+ months, best-performing ads deleted.
- **Q3 Desperate specificity.** Bet: the agency owner holding client accounts. Evidence: "A Business Portfolio I manage was hacked in June, and $10K was spent on a client's ad account"; "Someone from our agency's Meta account got hacked"; "a client that one of their staff (who was an admin on the ad account) had been hacked"; the $60k case entered through "a legacy agency account that a staff member had added years ago and never removed"; the MCC hijack wave targets agencies. The solo shop owner is the largest group ($1,129.89 balloon decor shop, "$500/month max" e-commerce) but shows up after the breach asking for refunds.
- **Q4 Narrowest wedge.** Bet: read-only connect, a "who holds the keys" audit, alerts in minutes. Evidence: the saashero guide's own recommendation is "alerts for suspicious activity, including new user additions and significant budget changes"; the Google Ads API exposes users, manager links, budgets and a change-event feed with about three minutes of lag (Codex, with Google's docs); Meta's side is unverified. "Apply all sec settings": no source shows an API to enforce 2FA or security settings on either platform, so at first it is a verified checklist.

Three quotes:

1. 2026-10-21, r/FacebookAds, small business owner: "Ad account hacked and charged $1,129.89 for a hacker's shoe ads. Meta has ignored my refund request for 2 weeks and PayPal denied my dispute." https://www.reddit.com/r/FacebookAds/comments/1xbex20/ad_account_hacked_and_charged_112989_for_a/
2. 2026-10-02, r/FacebookAds, agency side: "A Business Portfolio I manage was hacked in June, and $10K was spent on a client's ad account... On Aug 27 they said it wo[uld be refunded]... it never arrived." https://www.reddit.com/r/FacebookAds/comments/1wvf9s4/meta_says_a_10k_refund_for_a_hacked_portfolio_was/
3. 2026-09-07, r/FacebookAds: "Two years ago my business portfolio got breached by hackers and I discovered that 3 weeks ago. They removed my 'full control' rights and assigned me to 'basic rights'. The hackers added their own creditcard to my ad account." https://www.reddit.com/r/FacebookAds/comments/1wa26h2/business_portfolio_hacked/

Landscape in three lines:

- No dedicated product for ad-account takeover monitoring was found; general account-takeover tools (DataDome, Okta, SpyCloud) do not touch ad platforms, and PPC tools (Optmyzr, Adalysis, about 99 to 208 USD/month) alert on performance, not security.
- Google side: a free change-history script (nilsrooijmans.com, up to a day of lag, 30-day lookback) and The Ad Spend (change notices to Slack, Google only). Meta side: Meta's own emails and a manual review of Business Settings; agencies sell "daily monitoring" and "security reviews" as services (bfj.digital 2025-12-11, saashero.net 2026-04-12).
- Trade press: Search Engine Land, "Google Ads MCC hijacks are surging" (late 2025, https://searchengineland.com/google-ads-mcc-hijacks-are-surging-465186), entry via lookalike invitations and OAuth prompts without a stolen password; other vectors named: session-cookie theft bypassing 2FA ("over $11,000 in ad spend gone within hours despite 2FA"), malicious Chrome extensions posing as ad tools, dormant partner accounts; the $60k-in-96-hours case: https://bfj.digital/insights/how-a-forgotten-account-cost-our-client--60k/

## Decisions

- **D1 Buyer.** Options: A the owner of a 5–20 person performance agency holding 10–50 client accounts in the agency's own Business Portfolio and MCC, the owner signs (recommended); B the freelance media buyer running 3–10 clients through a personal profile; C the small-business owner spending $500–5k/month; D the in-house marketing manager at a $50k+/month brand. Vlad: "Agency owner (Recommended)". Recorded: buyer = owner of a small performance agency holding 10–50 client ad accounts; signer = the agency owner. Mark: `accepted recommendation`.
- **D2 Status quo and its cost.** Options: A manual checks on top of 2FA (recommended); B set-and-forget settings (2FA, caps and card limits once, no checks); C the free Google Ads script, nothing on Meta; D nothing until the breach. Vlad: "Set-and-forget settings". Pushed once: the late-discovery posts support him, the agencies describing daily monitoring are selling it; consequence: no labour is saved, the value is detection in minutes for someone who believes it will not happen to them. Recorded: status quo = 2FA and spend caps set once, nobody looks again, the takeover is found when the money is gone or the platform restricts the account; cost = the breach itself, $1.1K–$60K of spend, weeks to months of refund work, the client's trust. Mark: `Vlad's call`.
- **D3 Narrowest wedge and price shape.** Options with their arithmetic: A 59 EUR/month per agency workspace, first run is the keys audit, alerts within minutes, 59 × 6 × 0.9 = 319 EUR (recommended); B 149 EUR one-shot lockdown audit, 149 × 1 × 0.9 = 134 EUR (201 if half re-buy); C 4 EUR per client account per month on a bet of 20 accounts, 80 × 6 × 0.9 = 432 EUR; D 99 EUR audit + 39 EUR/month, (99 + 39 × 6) × 0.9 = 300 EUR. Vlad: "59/month per workspace (Recommended)". Mark: `accepted recommendation`, then revised at D5.
- **D4 Geo and language.** Options: A US + GB, English (recommended); B US only; C GB + IE + AU + NZ; D FR in French. Vlad: "US + UK, English (Recommended)". Recorded: geo = US,GB; language = en. Mark: `accepted recommendation`.
- **D5 Revision after the second opinion (premise 3).** Options: keep 59/month and confirm the shape at the challenge (recommended); revise to the 149 one-shot; revise to 99 + 39/month. Vlad typed: "revise to 599 manual +automatic audit (optional) + 59 / month". Pushed once: the manual audit puts founder hours inside the price (three hours at 100 EUR/h is half of 599, a service margin near 0.5), "optional" hangs its value on an unmeasured attach rate, and a cold click sees two prices. Recorded: price shape = optional 599 EUR manual + automatic lockdown audit, plus the 59 EUR/month watchdog; value per customer = 319 EUR (59 × 6 × 0.9, Vlad's price, default six months) + 99 EUR (599 × 0.33 attach rate × 0.5 margin, both my bets) = 418 EUR, provisional. Mark: `Vlad's call`.
- **Defaults kept:** cash cap 300 EUR, founder rate 100 EUR/h. Q1 was not asked; the position is in Homework.

## Premises

Asked in one question; Vlad: "Agree with all five".

1. The buyer is the owner of a 5–20 person performance agency who holds 10–50 client accounts in the agency's own Meta Business Portfolio and Google Ads MCC, and signs for the agency. Agreed.
2. Today they switch on 2FA and spend caps once and never look again; a takeover is discovered when the money is gone or the platform restricts the account, and the cost is the breach itself: $1K–$60K of fraudulent spend, weeks to months of refund work, and the client's trust. Agreed.
3. They would pay 59 EUR per month per workspace for a read-only watchdog whose first run is a full keys audit and that alerts within minutes on a new user or partner, a role change, a new payment method or a budget jump; value per customer 319 EUR on six paying months. Agreed, then **revised** after the second opinion, in his words: "revise to 599 manual +automatic audit (optional) + 59 / month".
4. The test runs in the US and the UK, in English, under the 300 EUR cash cap and the 100 EUR/h founder rate. Agreed.
5. Demand for prevention is unproven: the sweep proves recovery pain only, so the buyer most likely to pay first is an agency that has already been burned once. Agreed.

## Second opinion

Model: Codex (codex-cli 0.163.0, `codex exec -s read-only --skip-git-repo-check`), prompt = the office-hours filesystem boundary, the context block (pitch, decisions with Vlad's quotes, evidence, agreed premises; no private context) and the startup-mode instructions verbatim. 38,751 tokens, a few cents on the configured key. Its stderr showed Codex's own MCP config failing auth against a NeuralBox endpoint; harmless, nothing of ours was sent there.

Verbatim output:

> 1. **Strongest version:** A security watchtower for agencies that hold the keys to dozens of client ad accounts. It maps who has access, flags dangerous changes, and gives the owner a clear action to take before fraudulent spend or a lockout becomes a client crisis.
>
> 2. **Most revealing answer:** "Set-and-forget settings." The opening is *access drift*: an old partner, departed employee, or newly privileged user that nobody reviews. Build the first "who holds the keys" audit around that.
>
> 3. **Premise I think is wrong:** "They would pay 59 EUR per month per workspace." The evidence shows costly breaches, not recurring demand. I'd believe this premise is wrong if, after seeing a real audit, 0–1 of 10 previously burned agency owners pays for month one while several ask to buy the audit once.
>
> 4. **48-hour prototype:** Build for **one Google Ads MCC and a few client accounts**: TypeScript, Next.js, Postgres, a scheduled worker, and email alerts. Take an initial snapshot of users, roles, manager links, and budgets; show risky access; compare later snapshots and alert on a new admin, new manager link, or large budget jump. Google exposes those records, though its change-event feed can lag by up to three minutes. [User access](https://developers.google.com/google-ads/api/docs/account-management/managing-users), [manager links](https://developers.google.com/google-ads/api/docs/account-management/linking-manager-accounts), [budgets](https://developers.google.com/google-ads/api/fields/v26/campaign_budget), [change-event delay](https://developers.google.com/google-ads/api/docs/change-event). Skip Meta integration, payment-method detection, automatic security-setting changes, and any guaranteed alert time. If production API access is pending, run the same audit and diff on pilot-provided snapshots; Google's test access cannot query production accounts. [Google API access levels](https://developers.google.com/google-ads/api/docs/api-policy/access-levels).

Synthesis:

- Agree on the wedge: access drift is the sharpest thing in the evidence (the $60k legacy account, "the impersonator has more permission than I do"); the first-run keys audit is the front door.
- Agree on feasibility on the Google side: users, manager links, budgets and a change-event feed with about three minutes of lag make "alerts within minutes" credible there.
- Disagree on skipping Meta in what is sold: fine for a 48-hour prototype, wrong for the ad test, since 16 of the 22 Reddit hits are Meta.
- On premise 3, half right: the sweep shows no recurring demand, but no one-shot demand either; Codex's ten-owner test is the right and cheap way to settle the shape.
- The challenged premise did not change the recommendation (keep 59/month, confirm at the challenge).

Revision decision: Vlad revised premise 3 to his own shape, "revise to 599 manual +automatic audit (optional) + 59 / month", neither Codex's one-shot nor the keep; recorded at D5 as `Vlad's call`.

## Claims checked

- "hackers taking over" ad accounts on Google Ads and Facebook Ads, today: `supported`. 22 Reddit hits in 90 days (lower bound), the MCC hijack wave in trade press, the $60k-in-96-hours agency case, the saashero anecdotes.
- "monitor proactively" through the platforms' APIs: `supported` for Google Ads (user access, manager links, budgets, change events with about three minutes of lag, per Google's docs cited by Codex); `unchecked (Meta API fields for business users, partners, funding sources and their latency not verified)` for Meta.
- "apply all sec settings" automatically: `weak`. No source shows an API to enforce 2FA or security settings on either platform; Codex skips "automatic security-setting changes"; a verified checklist until the triage proves otherwise.
- "etc." (TikTok, LinkedIn, Microsoft and other networks): `unchecked (not swept; the sweep covered Meta and Google only)`.
- Someone advertises for this: `deferred to triage`.
- Someone pays for this, prevention rather than recovery: `deferred to triage`; no paid prevention product appeared in the sweep.

## To confirm

- Price shape and the audit's attach rate: Codex's test at the challenge, a real audit shown to ten burned agency owners; what settles it is how many pay month one against how many buy the audit once. The floor without the audit is 319 EUR.
- Audit margin (bet 0.5, three founder hours at 100 EUR/h against 599 EUR): settled by timing the first manual audit.
- Six paying months of retention: the factory default, settled only after launch.
- Meta coverage: whether the Marketing and Business APIs expose users, partners, roles, funding sources and budget changes with usable latency; settled at triage from the docs and at the challenge by a probe on a personal Business Portfolio.
- "Apply settings" automation on either platform: settled at triage from the API docs.
- The buyer's account count (10–50) and the set-and-forget status quo: settled by the two conversations of the assignment.
- `provisional=true` until the price shape is confirmed.
