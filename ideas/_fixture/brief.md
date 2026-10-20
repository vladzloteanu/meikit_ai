# Brief — Fixture idea (dry runs only)

Triage of 2026-10-14. Canned data: every advertiser, price, count and quote below is invented.

## Summary

Independent dog groomers in France are reached today by three advertised booking tools at 15 to 29 EUR a month, and they complain in public about no-shows. The pain is visible and a price point exists. Triage score 4 of 6, gate PASS.

## Who pays today

| Advertiser | Where seen | Promise | Price | Offer shape |
|---|---|---|---|---|
| booking-tool-a.example | search ad | "Online booking for groomers" | 19 EUR/month | self-serve trial |
| salon-planner-b.example | social feed ad | "Fewer no-shows, automatic reminders" | 29 EUR/month | demo call |
| groomer-app-c.example | search ad | "Your agenda, free for 14 days" | 15 EUR/month | self-serve trial |

## Demand

| Bucket | Keywords | Monthly volume | Median CPC |
|---|---|---|---|
| solution_aware | 6 | 1,900 | 1.10 EUR |
| problem_aware | 5 | 640 | 0.45 EUR |
| trigger | 4 | 210 | 0.90 EUR |
| adjacent_budget | 5 | 1,200 | 0.60 EUR |

Top keywords: `logiciel toilettage chien` (480 a month, 1.30 EUR), `agenda toiletteur` (320, 0.95 EUR), `prise de rendez-vous toiletteur` (210, 1.10 EUR). CPC range 0.45 to 1.30 EUR.

## Complaints

9 threads in the last 12 months mention no-shows or evening booking messages; 2 in the last 30 days.

- "Three no-shows this week, that is a day of income gone." (https://forum.example/t/101)
- "I answer booking texts until 11 pm." (https://forum.example/t/102)
- "A deposit would fix it but I have no tool for it." (https://forum.example/t/103)

## Landscape

- Incumbents: booking-tool-a.example and salon-planner-b.example, both generic salon tools with a groomer landing page.
- Free alternatives: a shared calendar plus a messaging app; deposits by bank transfer.
- Institutional alternatives: none found.

## AdsInsights conclusions

Category resolved: pet services (invented). France, social feed: 14 advertisers, the three largest hold 61 % of reach (28 %, 19 %, 14 %). Typical hooks: remove the no-shows, free your evenings, one link for all your bookings.

## Triage score

| Signal | Score (0-2) | Evidence |
|---|---|---|
| pays_today | 2 | three advertisers buy French search or feed ads for this buyer |
| trigger | 1 | four trigger keywords, 210 searches a month, CPC 0.90 EUR |
| complaints | 1 | 9 threads in 12 months, 2 in the last 30 days |

## Gate

PASS: at least one score is 1 or more.

## Open questions for the challenge

- Is the buyer the salon owner, or the head office of a franchise?
- Does 19 EUR a month hold against a 29 EUR incumbent that also sends reminders?
- Can a refundable deposit be shown in the fake door without a payment account?

## Cost and time of this triage

0.40 EUR cash: 12 searchapi calls (0.12 EUR) and 1 neuralbox call (0.28 EUR). 38 minutes, inside the 60 minute and 3 EUR timebox.
