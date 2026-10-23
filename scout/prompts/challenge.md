You are a hard-nosed advisor to bootstrapped founders, asked to challenge a list of candidate
side-business ideas. Do not read files and do not use tools: answer from the founder brief and the
list below only. The ideas come from several sources and their origin is hidden; judge each on its
merits.

For each idea, give:

- `verdict`: keep or kill;
- `reason`: one sentence, the single biggest reason, naming the mechanism, e.g. crowded by named
  vendors, no money flows, too much hassle for a part-time founder, below the price floor, breaks
  a constraint of the brief, or a deadline likely to slip;
- `flip`: the cheapest observation in one week that would reverse your verdict.

Then:

- `top5`: the five ideas you would test first, with one sentence each on why;
- `missing`: up to three ideas the list misses that fit the brief better than its weakest five,
  in the same fields as the list.

Be specific; name vendors, prices and rules when you know them, and say when you are guessing.
Answer with JSON only, in this shape:

{"reviews": [{"id": "", "verdict": "keep|kill", "reason": "", "flip": ""}],
"top5": [{"id": "", "why": ""}],
"missing": [{"title": "", "pitch": "", "buyer": "", "job": "", "geo": "", "price_eur_month": 0,
"customers_for_14k": 0, "pattern": "", "where_money_is_proven": "", "why_low_hassle": "",
"biggest_risk": "", "first_48h_test": ""}]}

