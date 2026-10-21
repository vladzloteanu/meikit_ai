import functools
import json
import time
from datetime import UTC, date, datetime

import httpx
import pytest

from factory import costs, secrets, toolbase
from factory.cli import main
from factory.http import FIXTURES, Client, ProviderError
from factory.providers import algolia_hn, arcticshift, firecrawl, rdap
from factory.tools import pricing_scan

TODAY = date(2026, 10, 21)
FIRECRAWL_KEY = "fc-test-key-123456"
PROVIDERS = (arcticshift, algolia_hn, firecrawl, rdap)
# One argv per tool that a dry run can answer from the fixtures.
DRY_RUNS = [
    ["reddit_mentions", "--terms", "ad account hacked", "--subreddits", "FacebookAds"],
    ["hn_mentions", "--terms", "ad account hacked"],
    ["pricing_scan", "--urls", "https://example.com"],
    ["domain_check", "--name", "meikit"],
]
DRY_RUN_IDS = [argv[0] for argv in DRY_RUNS]
FREE = [argv for argv in DRY_RUNS if argv[0] != "pricing_scan"]


@pytest.fixture(autouse=True)
def frozen_today(monkeypatch):
    """Today is 2026-10-21: the default ranges and the selftests are dated from it."""
    monkeypatch.setattr(toolbase, "today", lambda: TODAY)


@pytest.fixture(autouse=True)
def slept(monkeypatch):
    """No test sleeps: the pacing and the backoffs are recorded instead."""
    seconds = []
    monkeypatch.setattr(time, "sleep", seconds.append)
    return seconds


@pytest.fixture
def no_secrets(monkeypatch):
    """Any read of a secret fails the test."""
    monkeypatch.setattr(secrets, "get", lambda *a, **k: pytest.fail("a secret was read"))


def ts(day: str) -> int:
    """The Unix time of midnight UTC starting `day` (YYYY-MM-DD)."""
    return int(datetime.fromisoformat(day).replace(tzinfo=UTC).timestamp())


def research(root, tool):
    return sorted((root / "ideas/_fixture/research").glob(f"{tool}_*"))


def fixture(name):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def wire(monkeypatch, module, handler):
    """Make `module.client()` build its real Client, talking to `handler` instead of the network.

    Returns the requests sent. The only secret it can read is the Firecrawl key."""
    seen = []

    def recording(request):
        seen.append(request)
        return handler(request)

    keys = {"providers.firecrawl.api_key": FIRECRAWL_KEY}
    monkeypatch.setattr(secrets, "get", lambda dotpath, *a, **k: keys[dotpath])
    monkeypatch.setattr(
        module, "Client", functools.partial(Client, transport=httpx.MockTransport(recording))
    )
    return seen


def answer(data, status=200, headers=None):
    return lambda request: httpx.Response(status, json=data, headers=headers)


def replay(*responses):
    """A handler answering each request with the next of `responses`."""
    queue = list(responses)
    return lambda request: queue.pop(0)


def run_json(capsys, argv):
    """Run `argv` with --json; its exit code must be 0. The research JSON it printed."""
    assert main([*argv, "--json"]) == 0
    return json.loads(capsys.readouterr().out)


def rule(*widths):
    return "  ".join("-" * width for width in widths)


# --- the brief's tests -------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("markdown", "prices"),
    [
        ("Pro $29/mo", ["$29/mo"]),
        ("à partir de 19 € par mois", ["19 € par mois"]),
        ("no digits", []),
    ],
)
def test_extract_prices(markdown, prices):
    assert pricing_scan.extract_prices(markdown) == prices


def test_guess_offer_shape():
    assert pricing_scan.guess_offer_shape(["$29/mo"], "") == "subscription"
    assert pricing_scan.guess_offer_shape([], "Contact sales for a quote") == "quote"


REGISTRY = "rdap.registry.example"
NO_SERVICE = {"errorCode": 404, "title": "No RDAP service is available for this resource"}


def rdap_org(answers):
    """A fake rdap.org: it redirects a lookup to the registry's RDAP server, which answers
    `answers[domain]` (a status, or a (status, body) pair); a domain whose answer is "none" gets
    rdap.org's own 404, as a TLD without an RDAP server does."""

    def handler(request):
        domain = request.url.path.rsplit("/", 1)[1]
        reply = answers[domain]
        if request.url.host == "rdap.org":
            if reply == "none":
                return httpx.Response(404, json=NO_SERVICE)
            location = f"https://{REGISTRY}/rdap/domain/{domain}"
            return httpx.Response(302, headers={"Location": location})
        status, body = reply if isinstance(reply, tuple) else (reply, {})
        return httpx.Response(status, json=body)

    return handler


def test_rdap_404_is_available(monkeypatch):
    seen = wire(monkeypatch, rdap, rdap_org({"zzqx-free-name.com": 404}))
    assert rdap.status(rdap.client(), "zzqx-free-name.com") == "available"
    asked = [(r.url.host, r.url.path) for r in seen]
    assert asked == [  # the registry's 404 is an answer, never retried
        ("rdap.org", "/domain/zzqx-free-name.com"),
        (REGISTRY, "/rdap/domain/zzqx-free-name.com"),
    ]


SLOW = {"data": None, "error": "Timeout. Maybe slow down a bit"}


class Clock:
    """A fake time.perf_counter, which httpx times each answer with (Response.elapsed)."""

    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.fixture
def clock(monkeypatch):
    """Answers last what the fake Arctic Shift says; no pacing, so `slept` holds only the
    search's own waits."""
    fake = Clock()
    monkeypatch.setattr(time, "perf_counter", fake)
    monkeypatch.setattr(arcticshift, "PACE_S", 0.0)
    return fake


def timed(clock, *replies):
    """A handler answering each request with the next (seconds, response) of `replies`: the
    request lasts that many seconds on `clock`."""
    queue = list(replies)

    def handler(request):
        took, response = queue.pop(0)
        clock.now += took
        return response

    return handler


class Streamed(httpx.SyncByteStream):
    """A body httpx reads as it reads a network one, so it times the answer (Response.elapsed);
    a body given as `json=` is read at once and never timed."""

    def __init__(self, body: bytes):
        self.body = body

    def __iter__(self):
        yield self.body


def slowed(reset=None):
    """Arctic Shift's 422, with X-RateLimit-Reset when `reset` is given."""
    headers = {} if reset is None else {"X-RateLimit-Reset": str(reset)}
    return httpx.Response(422, headers=headers, stream=Streamed(json.dumps(SLOW).encode()))


def data(*items):
    return httpx.Response(200, json={"data": [raw(item) for item in items]})


def test_arctic_shift_slow_down_is_waited_out_then_the_same_window_answers(
    root, capsys, monkeypatch, clock, slept
):
    # the brief's case: a fast 422 is a throttle; the search sleeps X-RateLimit-Reset seconds
    # and asks the same window again, which answers one result
    one = post("1wyvibe", "2026-10-05", title="Ads account hacked")
    replies = [(0.4, slowed(12)), (5.5, data(one)), (0.5, data())]
    seen = wire(monkeypatch, arcticshift, timed(clock, *replies))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    out = run_json(capsys, [*argv, *RANGE])
    whole = ("2026-08-01", "2026-10-21")
    assert asked(seen) == [("posts", *whole), ("posts", *whole), ("comments", *whole)]
    assert slept == [12]
    term = out["terms"]["x"]
    assert (term["posts"], term["comments"], term["complete"]) == (1, 0, True)
    assert (term["calls"], term["waited_s"]) == (3, 12)
    assert term["hits"][0]["title"] == "Ads account hacked"


# --- prices and offers -------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "prices"),
    [
        ("$29", ["$29"]),
        ("$29/mo", ["$29/mo"]),
        ("29 €", ["29 €"]),
        ("29€/mois", ["29€/mois"]),
        ("€29 per month", ["€29 per month"]),
        ("29 EUR", ["29 EUR"]),
        ("From $19", ["$19"]),
        ("$1,299.99 a year", ["$1,299.99 a year"]),
        ("Équipe : 1 299 € HT / mois", ["1 299 € HT / mois"]),
        ("£12 per seat per month", ["£12 per seat per month"]),
        ("Solo $29/mo, Team $99/user/month, Solo $29/mo", ["$29/mo", "$99/user/month"]),
        ("Version 2.5 of 2026: 30 days free, 4.9/5 stars", []),
        # a currency after an amount is not followed by a digit: "1 $" is no price
        ("Tier 1 $9/mo, Tier 2 $29/mo", ["$9/mo", "$29/mo"]),
        ("Tier 1 $ 9/mo", ["$ 9/mo"]),
        # an amount starts after neither a digit nor a letter: not "026 150" inside "2026 150";
        # HT stays, since a price before VAT is 20 % less than one with it
        ("Offre 2026 150 € HT", ["150 € HT"]),
        ("Pack A29 €, Pack2 39 €", ["39 €"]),
    ],
)
def test_extract_prices_reads_each_way_a_price_is_written(text, prices):
    assert pricing_scan.extract_prices(text) == prices


@pytest.mark.parametrize(
    ("prices", "markdown", "shape"),
    [
        (["$29/mo"], "", "subscription"),
        (["19 € par mois"], "", "subscription"),
        (["$290/yr"], "", "subscription"),
        # what the 40 characters after a price say counts...
        (["$29"], "Solo $29, billed monthly, cancel anytime.", "subscription"),
        (["$29"], "Pro: $29 every month", "subscription"),
        (["29 €"], "Formule 29 € le mois", "subscription"),
        # ...never what the page says elsewhere
        (["$29"], "Billed monthly. Solo: $29.", "one_shot"),
        (["$29"], "Solo $29." + " filler" * 6 + " Billed monthly.", "one_shot"),
        # a negation next to the marker: not a subscription
        (["$199"], "Lifetime: $199, no monthly fees.", "one_shot"),
        (["49 €"], "Licence 49 € sans abonnement mensuel", "one_shot"),
        (["$29"], "Solo $29. No setup fee. Billed monthly.", "subscription"),
        (["$199"], "Pay once, use it forever.", "one_shot"),
        (["$499"], "Enterprise? Contact sales.", "one_shot"),
        ([], "Contact sales for a quote", "quote"),
        ([], "Tarifs sur devis", "quote"),
        ([], "Talk to our sales team", "quote"),
        ([], "The watchdog for your ad accounts", "unknown"),
    ],
)
def test_guess_offer_shape_by_recurring_prices_then_quotes(prices, markdown, shape):
    assert pricing_scan.guess_offer_shape(prices, markdown) == shape


@pytest.mark.parametrize(
    ("markdown", "headline"),
    [
        # the H1, wherever it is, as plain text
        (
            "Intro\n\n## Pricing\n\n# **Stop** ad account [takeovers](https://x.example)\n",
            "Stop ad account takeovers",
        ),
        ("### Small print\n\n## Plans for teams ##\n\n## Other\n", "Plans for teams"),
        ("No heading at all\n\n#hashtag", None),
    ],
)
def test_headline_is_the_first_heading_of_the_highest_level(markdown, headline):
    assert pricing_scan.headline(markdown) == headline


@pytest.mark.parametrize(
    ("markdown", "cta"),
    [
        ("[Log in](/login) [Start free trial](/signup) [Book a demo](/demo)", "Start free trial"),
        ("[![logo](/logo.png)](/) and [Essai gratuit 14 jours](/essai)", "Essai gratuit 14 jours"),
        ("[Talk to **sales**](/sales)", "Talk to sales"),
        ("[Starter](/plans/starter) [Get started](/signup)", "Get started"),
        ("[Facebook](/fb) [Essayez gratuitement](/essai)", "Essayez gratuitement"),
        ("[Tarifs](/tarifs) [Demander une démo](/demo)", "Demander une démo"),
        ("[Learn more](/more), Start free trial today", None),
    ],
)
def test_cta_is_the_first_call_to_action_link(markdown, cta):
    assert pricing_scan.cta(markdown) == cta


# --- the providers against a mock transport ----------------------------------------------------


def test_arcticshift_searches_the_posts_and_comments_of_a_subreddit(monkeypatch):
    seen = wire(monkeypatch, arcticshift, answer({"data": [{"id": "a"}, "not an item"]}))
    c = arcticshift.client()
    found = arcticshift.posts_search(
        c,
        "ad account hacked",
        subreddit="FacebookAds",
        after="2025-10-21",
        before="2026-10-22",
        limit=50,
    )
    assert found == [{"id": "a"}]
    assert arcticshift.comments_search(c, "ad account hacked", subreddit="PPC") == [{"id": "a"}]
    assert [(r.method, r.url.host, r.url.path) for r in seen] == [
        ("GET", "arctic-shift.photon-reddit.com", "/api/posts/search"),
        ("GET", "arctic-shift.photon-reddit.com", "/api/comments/search"),
    ]
    assert dict(seen[0].url.params) == {
        "query": "ad account hacked",
        "subreddit": "FacebookAds",
        "after": "2025-10-21",
        "before": "2026-10-22",
        "limit": "50",
        "sort": "desc",
    }  # no `fields`: Arctic Shift refuses `permalink` in it, and only whole items carry one
    assert dict(seen[1].url.params) == {
        "body": "ad account hacked",
        "subreddit": "PPC",
        "limit": "100",
        "sort": "desc",
    }
    assert c.pace_s == 1.0 and c.retry_on is None  # a 422 is the search's to handle


def test_arcticshift_slow_down_is_a_422_saying_so():
    assert arcticshift.slow_down(
        httpx.Response(422, text='{"error":"Timeout. Maybe slow down a bit"}')
    )
    assert not arcticshift.slow_down(httpx.Response(422, text='{"error":"Invalid sort"}'))
    assert not arcticshift.slow_down(httpx.Response(400, text="slow down"))


def test_an_arcticshift_422_raises_slow_down_at_once_with_its_reset(monkeypatch, clock, slept):
    seen = wire(monkeypatch, arcticshift, timed(clock, (0.4, slowed(12))))
    with pytest.raises(arcticshift.SlowDown) as e:
        arcticshift.comments_search(arcticshift.client(), "x", subreddit="PPC")
    assert isinstance(e.value, ProviderError)
    assert (e.value.status, e.value.reset_s, len(seen), slept) == (422, 12.0, 1, [])
    assert (e.value.took_s, e.value.throttled) == (0.4, True)  # fast: the throttle
    assert str(e.value).startswith("arcticshift: HTTP 422: GET /api/comments/search?body=x&")
    assert str(e.value).endswith('Timeout. Maybe slow down a bit"}')


@pytest.mark.parametrize(("took", "throttled"), [(4.99, True), (5.0, False), (11.0, False)])
def test_a_422_that_took_5_s_or_more_is_a_timeout(monkeypatch, clock, took, throttled):
    wire(monkeypatch, arcticshift, timed(clock, (took, slowed(5))))
    with pytest.raises(arcticshift.SlowDown) as e:
        arcticshift.posts_search(arcticshift.client(), "x", subreddit="PPC")
    assert (e.value.took_s, e.value.throttled) == (pytest.approx(took), throttled)


@pytest.mark.parametrize(
    ("headers", "reset"),
    [
        ({}, None),
        ({"X-RateLimit-Reset": "soon"}, None),
        ({"X-RateLimit-Reset": "-5"}, 0.0),
        ({"X-RateLimit-Reset": "7.5"}, 7.5),
        ({"X-RateLimit-Reset": "1800000050"}, 50.0),  # a Unix time: 50 s from now
    ],
)
def test_slow_down_carries_the_reset_seconds_arctic_shift_sent(monkeypatch, headers, reset):
    monkeypatch.setattr(time, "time", lambda: 1_800_000_000.0)
    wire(monkeypatch, arcticshift, answer(SLOW, status=422, headers=headers))
    with pytest.raises(arcticshift.SlowDown) as e:
        arcticshift.posts_search(arcticshift.client(), "x", subreddit="PPC")
    assert e.value.reset_s == reset


def test_an_arcticshift_5xx_is_retried(monkeypatch):
    replies = replay(httpx.Response(503), httpx.Response(200, json={"data": [{"id": "a"}]}))
    seen = wire(monkeypatch, arcticshift, replies)
    assert arcticshift.posts_search(arcticshift.client(), "x", subreddit="PPC") == [{"id": "a"}]
    assert len(seen) == 2


def test_arcticshift_refusal_is_one_provider_error_without_retry(monkeypatch):
    refusal = {"data": None, "error": "'query' query parameter requires one of: author, subreddit"}
    seen = wire(monkeypatch, arcticshift, answer(refusal, status=400))
    with pytest.raises(ProviderError) as e:
        arcticshift.posts_search(arcticshift.client(), "ad account hacked")
    assert e.value.status == 400 and "requires one of: author, subreddit" in str(e.value)
    assert len(seen) == 1


def test_algolia_searches_by_date_without_typo_tolerance(monkeypatch):
    seen = wire(monkeypatch, algolia_hn, answer({"hits": [], "nbHits": 0}))
    c = algolia_hn.client()
    answered = algolia_hn.search_by_date(
        c, "ad account", "comment", 1761004800, 1792627200, hits_per_page=20
    )
    assert answered == {"hits": [], "nbHits": 0}
    [request] = seen
    assert (request.url.host, request.url.path) == ("hn.algolia.com", "/api/v1/search_by_date")
    assert dict(request.url.params) == {
        "query": "ad account",
        "tags": "comment",
        "numericFilters": "created_at_i>1761004800,created_at_i<1792627200",
        "hitsPerPage": "20",
        "typoTolerance": "false",
    }
    assert c.pace_s == 0.2


def test_firecrawl_scrapes_the_main_content_as_markdown_with_the_bearer_key(monkeypatch):
    data = {"markdown": "# Hello", "metadata": {"title": "Hello", "statusCode": 200}}
    seen = wire(monkeypatch, firecrawl, answer({"success": True, "data": data}))
    assert firecrawl.scrape(firecrawl.client(), "https://example.com") == data
    [request] = seen
    assert (request.method, request.url.host, request.url.path) == (
        "POST",
        "api.firecrawl.dev",
        "/v1/scrape",
    )
    assert json.loads(request.content) == {
        "url": "https://example.com",
        "formats": ["markdown"],
        "onlyMainContent": True,
    }
    assert request.headers["Authorization"] == f"Bearer {FIRECRAWL_KEY}"


def test_a_firecrawl_error_never_shows_the_key(monkeypatch):
    refusal = {"success": False, "error": f"Unauthorized: invalid token Bearer {FIRECRAWL_KEY}"}
    wire(monkeypatch, firecrawl, answer(refusal, status=401))
    config = {"providers": {"firecrawl": {"api_key": FIRECRAWL_KEY}}}
    monkeypatch.setattr(secrets, "load", lambda *a, **k: config)
    with pytest.raises(ProviderError) as e:
        firecrawl.scrape(firecrawl.client(), "https://example.com")
    assert e.value.status == 401 and FIRECRAWL_KEY not in str(e.value)


@pytest.mark.parametrize(
    ("reply", "expected", "registry_asked"),
    [
        ((200, {"objectClassName": "domain", "ldhName": "EXAMPLE.COM"}), "taken", 1),
        ((404, {"errorCode": 404, "title": "Not Found"}), "available", 1),
        (404, "available", 1),
        # the registry answered: what its body says does not matter
        ((404, NO_SERVICE), "available", 1),
        # rdap.org's own 404, for a TLD without an RDAP server (.io): nothing about the domain
        ("none", "unknown", 0),
        ((400, {"errorCode": 400}), "unknown", 1),
        (503, "unknown", 3),  # retried, then given up
    ],
)
def test_rdap_status_reads_the_registry_answer(monkeypatch, reply, expected, registry_asked):
    seen = wire(monkeypatch, rdap, rdap_org({"example.com": reply}))
    assert rdap.status(rdap.client(), "example.com") == expected
    assert str(seen[0].url) == "https://rdap.org/domain/example.com"
    assert sum(1 for r in seen if r.url.host == REGISTRY) == registry_asked


def test_rdap_org_answering_404_itself_is_unknown_whatever_it_says(monkeypatch):
    # no redirect: rdap.org answered, not a registry, so its 404 says nothing about the domain
    seen = wire(monkeypatch, rdap, answer({"errorCode": 404, "title": "Not Found"}, status=404))
    assert rdap.status(rdap.client(), "example.io") == "unknown" and len(seen) == 1


def test_an_rdap_dry_run_takes_a_com_and_frees_the_rest(no_secrets):
    c = rdap.client(dry_run=True)
    statuses = [rdap.status(c, domain) for domain in ("example.com", "example.io", "x.fr")]
    assert statuses == ["taken", "available", "available"] and c.calls == 3


# --- every tool --------------------------------------------------------------------------------


def test_the_voc_tools_are_registered(capsys):
    assert main(["--help"]) == 0
    out = capsys.readouterr().out
    assert all(tool in out for tool in DRY_RUN_IDS)


@pytest.mark.parametrize("argv", DRY_RUNS, ids=DRY_RUN_IDS)
def test_a_dry_run_writes_research_reads_no_key_and_logs_nothing(root, capsys, no_secrets, argv):
    log = root / "ideas/_fixture/costs.jsonl"
    before = log.read_text(encoding="utf-8")
    assert main([*argv, "--idea", "_fixture", "--dry-run"]) == 0
    [path] = research(root, argv[0])
    assert path.name.endswith(".dryrun.json")
    assert json.loads(path.read_text(encoding="utf-8"))["dry_run"] is True
    assert log.read_text(encoding="utf-8") == before
    out, err = capsys.readouterr()
    assert out.strip()
    assert err.startswith(f"{argv[0]}: dry run: wrote ideas/_fixture/research/{argv[0]}_")


@pytest.mark.parametrize("argv", DRY_RUNS, ids=DRY_RUN_IDS)
def test_an_unknown_idea_is_refused_before_any_client(root, capsys, monkeypatch, argv):
    for module in PROVIDERS:
        monkeypatch.setattr(module, "client", lambda dry_run=False: pytest.fail("client built"))
    assert main([*argv, "--idea", "nope"]) == 1
    err = capsys.readouterr().err
    assert err.startswith(f"{argv[0]}: no idea 'nope' in ideas/") and err.count("\n") == 1


@pytest.mark.parametrize("argv", FREE, ids=[argv[0] for argv in FREE])
def test_a_free_tool_logs_no_cost(root, capsys, monkeypatch, argv):
    for module, reply in (
        (arcticshift, answer({"data": []})),
        (algolia_hn, answer({"hits": [], "nbHits": 0})),
        (rdap, answer({}, status=404)),
    ):
        wire(monkeypatch, module, reply)
    monkeypatch.setattr(secrets, "get", lambda *a, **k: pytest.fail("a free tool read a secret"))
    log = root / "ideas/_fixture/costs.jsonl"
    before = log.read_text(encoding="utf-8")
    assert main([*argv, "--idea", "_fixture"]) == 0
    assert log.read_text(encoding="utf-8") == before
    [path] = research(root, argv[0])
    assert path.name.endswith(".json") and not path.name.endswith(".dryrun.json")
    assert capsys.readouterr().err == f"{argv[0]}: wrote ideas/_fixture/research/{path.name}\n"


def test_pricing_scan_without_the_master_key_stops_on_one_line(root, capsys):
    assert main(["pricing_scan", "--idea", "_fixture", "--urls", "https://example.com"]) == 1
    out, err = capsys.readouterr()
    assert out == "" and "make secrets-init" in err and err.count("\n") == 1
    assert research(root, "pricing_scan") == []


@pytest.mark.parametrize("tool", DRY_RUN_IDS)
def test_a_selftest_dry_run_answers_from_the_fixtures(root, capsys, no_secrets, tool):
    posts = len(fixture("arcticshift/posts_search")["data"])
    stories = len(fixture("algolia/search_by_date")["hits"])
    line = {
        "reddit_mentions": f"OK arcticshift {posts} items",
        "hn_mentions": f"OK algolia {stories} items",
        "pricing_scan": "OK firecrawl 1 items",
        "domain_check": "OK rdap 1 items",
    }[tool]
    assert main([tool, "--selftest", "--dry-run"]) == 0
    assert capsys.readouterr().out == f"{line}\n"


YEAR_START, YEAR_END = ts("2025-10-21"), ts("2026-10-22")  # the 12 months up to TODAY
SELFTESTS = [
    (
        "reddit_mentions",
        arcticshift,
        answer({"data": [{"id": "a"}, {"id": "b"}]}),
        "OK arcticshift 2 items",
        (
            "GET",
            "/api/posts/search",
            {
                "query": "ad account",
                "subreddit": "FacebookAds",
                "after": "2026-09-21",
                "limit": "10",
                "sort": "desc",
            },
        ),
    ),
    (
        "hn_mentions",
        algolia_hn,
        answer({"hits": [{"objectID": "1"}], "nbHits": 1}),
        "OK algolia 1 items",
        (
            "GET",
            "/api/v1/search_by_date",
            {
                "query": "ad account",
                "tags": "story",
                "numericFilters": f"created_at_i>{YEAR_START - 1},created_at_i<{YEAR_END}",
                "hitsPerPage": "10",
                "typoTolerance": "false",
            },
        ),
    ),
    (
        "pricing_scan",
        firecrawl,
        answer({"success": True, "data": {"markdown": "Example", "metadata": {"title": "E"}}}),
        "OK firecrawl 1 items",
        ("POST", "/v1/scrape", {}),
    ),
    (
        "domain_check",
        rdap,
        answer({"objectClassName": "domain"}),
        "OK rdap 1 items",
        ("GET", "/domain/example.com", {}),
    ),
]


@pytest.mark.parametrize(
    ("tool", "module", "reply", "line", "asked"), SELFTESTS, ids=[s[0] for s in SELFTESTS]
)
def test_a_selftest_is_one_call_that_writes_and_logs_nothing(
    root, capsys, monkeypatch, tool, module, reply, line, asked
):
    seen = wire(monkeypatch, module, reply)
    log = root / "ideas/_fixture/costs.jsonl"
    before = log.read_text(encoding="utf-8")
    assert main([tool, "--selftest"]) == 0
    assert capsys.readouterr().out == f"{line}\n"
    assert [(r.method, r.url.path, dict(r.url.params)) for r in seen] == [asked]
    assert research(root, tool) == [] and log.read_text(encoding="utf-8") == before


def test_the_pricing_scan_selftest_scrapes_example_com(monkeypatch, capsys):
    seen = wire(monkeypatch, firecrawl, SELFTESTS[2][2])
    assert main(["pricing_scan", "--selftest"]) == 0
    assert json.loads(seen[0].content)["url"] == "https://example.com"


def test_a_domain_check_selftest_finding_example_com_free_fails(root, capsys, monkeypatch):
    wire(monkeypatch, rdap, rdap_org({"example.com": 404}))
    assert main(["domain_check", "--selftest"]) == 1
    out, err = capsys.readouterr()
    assert out == "" and err == "domain_check: rdap: example.com came back available, not taken\n"


# --- reddit_mentions ---------------------------------------------------------------------------


def post(id_, day, subreddit="FacebookAds", at=3600, **fields):
    return {
        "kind": "post",
        "id": id_,
        "created_utc": ts(day) + at,
        "subreddit": subreddit,
        "author": "user1",
        "title": f"post {id_}",
        "selftext": "",
        "score": 1,
        "num_comments": 0,
        **fields,
    }


def comment(id_, day, subreddit="FacebookAds", link="p1", **fields):
    return {
        "kind": "comment",
        "id": id_,
        "created_utc": ts(day) + 3600,
        "subreddit": subreddit,
        "author": "user2",
        "body": f"comment {id_}",
        "link_id": f"t3_{link}",
        "score": 1,
        **fields,
    }


ITEMS = [
    post(
        "p1",
        "2026-10-05",
        title="Ad account hacked again",
        selftext="My ad account  got\nhacked.",
        score=5,
    ),
    # exactly on the boundary of two windows: both answer it, it counts once
    post("p2", "2026-09-30", at=0, title="Hacked business manager", selftext="[removed]"),
    comment("c1", "2026-10-06", body="Same here, my ad account was hacked", score=3),
    comment("c2", "2026-10-06", body="[deleted]"),
    comment("c3", "2026-10-07", author="AutoModerator", body="Hacked? Read the wiki first."),
    comment("c4", "2026-10-08", body="I am a bot, and this action was performed automatically."),
    comment(
        "c5", "2026-08-15", subreddit="PPC", link="zz9", body="Ad account hacked last week", score=2
    ),
]
RANGE = ["--since", "2026-08-01", "--until", "2026-10-20"]


def raw(item):
    """An item of ITEMS as Arctic Shift answers it, without the fake's `kind`."""
    return {key: value for key, value in item.items() if key != "kind"}


def asked(seen):
    """(kind, after, before) of each Arctic Shift search sent."""
    return [(r.url.path.split("/")[2], r.url.params["after"], r.url.params["before"]) for r in seen]


def arctic(items):
    """A fake Arctic Shift over `items`: a search answers the items of its kind and subreddit
    created from `after` to `before`, both included, newest first, at most `limit` of them."""

    def handler(request):
        params = request.url.params
        kind = "post" if request.url.path == "/api/posts/search" else "comment"
        found = [
            {key: value for key, value in item.items() if key != "kind"}
            for item in items
            if item["kind"] == kind
            and item["subreddit"].lower() == params["subreddit"].lower()
            and ts(params["after"]) <= item["created_utc"] <= ts(params["before"])
        ]
        found.sort(key=lambda item: -item["created_utc"])
        return httpx.Response(200, json={"data": found[: int(params["limit"])]})

    return handler


def test_reddit_mentions_searches_each_term_subreddit_and_kind_once_over_the_range(
    root, capsys, monkeypatch
):
    seen = wire(monkeypatch, arcticshift, answer({"data": []}))
    argv = [
        "reddit_mentions",
        "--idea",
        "_fixture",
        "--terms",
        "x",
        "--subreddits",
        "r/FacebookAds,PPC",
    ]
    out = run_json(capsys, [*argv, *RANGE])
    whole = ("2026-08-01", "2026-10-21")  # --until is included
    assert [(r.url.params["subreddit"], *a) for r, a in zip(seen, asked(seen), strict=True)] == [
        ("FacebookAds", "posts", *whole),  # r/ is dropped
        ("FacebookAds", "comments", *whole),
        ("PPC", "posts", *whole),
        ("PPC", "comments", *whole),
    ]
    assert {(r.url.params["limit"], r.url.params["sort"]) for r in seen} == {("100", "desc")}
    assert {r.url.params["query" if "posts" in r.url.path else "body"] for r in seen} == {"x"}
    term = out["terms"]["x"]
    assert (term["complete"], term["covered_since"]) == (True, "2026-08-01")
    assert (term["calls"], term["waited_s"]) == (4, 0)


def test_reddit_mentions_default_range_is_the_12_months_up_to_today(root, capsys, monkeypatch):
    seen = wire(monkeypatch, arcticshift, answer({"data": []}))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    out = run_json(capsys, argv)
    assert (out["since"], out["until"]) == ("2025-10-21", "2026-10-21")
    assert asked(seen) == [
        ("posts", "2025-10-21", "2026-10-22"),
        ("comments", "2025-10-21", "2026-10-22"),
    ]


def test_reddit_mentions_counts_by_month_and_subreddit_and_keeps_the_newest_hits(
    root, capsys, monkeypatch
):
    wire(monkeypatch, arcticshift, arctic(ITEMS))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "ad account hacked"]
    out = run_json(capsys, [*argv, "--subreddits", "FacebookAds,PPC", *RANGE])
    assert out == {
        "subreddits": ["FacebookAds", "PPC"],
        "since": "2026-08-01",
        "until": "2026-10-20",
        "limit": 100,
        "max_wait_s": 300,
        "waited_s": 0.0,
        "skipped_searches": 0,
        "terms": {
            "ad account hacked": {
                "posts": 2,
                "comments": 2,
                "by_month": {"2026-08": 1, "2026-09": 1, "2026-10": 2},
                "by_subreddit": {"FacebookAds": 3, "PPC": 1},
                "complete": True,
                "covered_since": "2026-08-01",
                "skipped": False,
                "calls": 4,
                "waited_s": 0.0,
                "hits": [
                    {
                        "kind": "comment",
                        "subreddit": "FacebookAds",
                        "title": None,
                        "url": "https://www.reddit.com/r/FacebookAds/comments/p1/comment/c1/",
                        "score": 3,
                        "created": "2026-10-06",
                        "snippet": "Same here, my ad account was hacked",
                    },
                    {
                        "kind": "post",
                        "subreddit": "FacebookAds",
                        "title": "Ad account hacked again",
                        "url": "https://www.reddit.com/r/FacebookAds/comments/p1/",
                        "score": 5,
                        "created": "2026-10-05",
                        "snippet": "My ad account got hacked.",
                    },
                    {
                        "kind": "post",
                        "subreddit": "FacebookAds",
                        "title": "Hacked business manager",
                        "url": "https://www.reddit.com/r/FacebookAds/comments/p2/",
                        "score": 1,
                        "created": "2026-09-30",
                        "snippet": None,
                    },
                    {
                        "kind": "comment",
                        "subreddit": "PPC",
                        "title": None,
                        "url": "https://www.reddit.com/r/PPC/comments/zz9/comment/c5/",
                        "score": 2,
                        "created": "2026-08-15",
                        "snippet": "Ad account hacked last week",
                    },
                ],
            }
        },
    }


def test_reddit_mentions_skips_an_item_without_an_id_or_a_sane_time(root, capsys, monkeypatch):
    items = [
        post("ok", "2026-10-02"),
        dict(post("noid", "2026-10-02"), id=None),
        dict(post("far", "2026-10-02"), created_utc=1e20),
        dict(post("nan", "2026-10-02"), created_utc=float("nan")),
        dict(post("bool", "2026-10-02"), created_utc=True),
    ]
    # json.dumps writes NaN, which JSON has not but Python's parser reads: a malformed answer
    body = json.dumps({"data": [{k: v for k, v in i.items() if k != "kind"} for i in items]})
    wire(monkeypatch, arcticshift, lambda request: httpx.Response(200, content=body.encode()))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "FacebookAds"]
    out = run_json(capsys, [*argv, "--since", "2026-10-01", "--until", "2026-10-20"])
    assert [hit["url"].split("/")[-2] for hit in out["terms"]["x"]["hits"]] == ["ok"]


def test_reddit_mentions_uses_the_permalink_an_item_carries(root, capsys, monkeypatch):
    item = post("p9", "2026-10-02", permalink="/r/FacebookAds/comments/p9/locked_out/")
    wire(monkeypatch, arcticshift, arctic([item]))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "FacebookAds"]
    [hit] = run_json(capsys, [*argv, *RANGE])["terms"]["x"]["hits"]
    assert hit["url"] == "https://www.reddit.com/r/FacebookAds/comments/p9/locked_out/"


def test_a_full_answer_ends_its_search_and_leaves_the_term_incomplete(root, capsys, monkeypatch):
    # 100 posts back: more exist, older than the oldest (2026-09-15 10:00), never asked for
    full = [raw(post(f"p{n}", "2026-09-15", at=36000 + n * 60)) for n in range(100)]
    seen = wire(
        monkeypatch,
        arcticshift,
        lambda request: httpx.Response(
            200, json={"data": full if "posts" in request.url.path else []}
        ),
    )
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    out = run_json(capsys, [*argv, *RANGE, "--limit", "3"])
    term = out["terms"]["x"]
    assert (term["posts"], term["comments"], term["complete"]) == (100, 0, False)
    assert term["covered_since"] == "2026-09-16"  # the first day fetched in full
    assert len(term["hits"]) == 3  # --limit caps the hits, not the search
    assert [kind for kind, _, _ in asked(seen)] == ["posts", "comments"]


@pytest.mark.parametrize(
    ("reset", "wait"),
    [(None, 3), (60, 60), (500, 120), (1_800_000_050, 50)],  # the last: a Unix time
)
def test_a_throttle_is_waited_out_in_full_up_to_120_s(
    root, capsys, monkeypatch, clock, slept, reset, wait
):
    monkeypatch.setattr(time, "time", lambda: 1_800_000_000.0)
    replies = [(0.3, slowed(reset)), (0.3, data()), (0.3, data())]
    seen = wire(monkeypatch, arcticshift, timed(clock, *replies))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    out = run_json(capsys, [*argv, *RANGE])
    assert slept == [wait] and len(seen) == 3
    assert (out["terms"]["x"]["complete"], out["terms"]["x"]["waited_s"]) == (True, wait)


def test_a_slow_422_is_a_timeout_and_halves_the_window(root, capsys, monkeypatch, clock, slept):
    replies = [(6.2, slowed(5)), (4.0, data()), (4.0, data()), (1.0, data())]
    seen = wire(monkeypatch, arcticshift, timed(clock, *replies))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    out = run_json(capsys, [*argv, *RANGE])
    assert asked(seen) == [
        ("posts", "2026-08-01", "2026-10-21"),  # 6.2 s: a timeout
        ("posts", "2026-09-10", "2026-10-21"),  # the newest half
        ("posts", "2026-08-01", "2026-09-10"),  # the older half
        ("comments", "2026-08-01", "2026-10-21"),
    ]
    assert slept == [5]  # its reset waited out before the halved window
    term = out["terms"]["x"]
    assert (term["complete"], term["calls"], term["waited_s"]) == (True, 4, 5)


def test_a_search_stops_when_its_8_calls_are_spent(root, capsys, monkeypatch, clock, slept):
    replies = [*[(0.3, slowed(10))] * 8, (0.3, data())]  # posts: throttled 8 times
    seen = wire(monkeypatch, arcticshift, timed(clock, *replies))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    out = run_json(capsys, [*argv, *RANGE])
    whole = ("2026-08-01", "2026-10-21")
    assert asked(seen) == [*[("posts", *whole)] * 8, ("comments", *whole)]  # the same window
    assert slept == [10] * 7  # no wait after the last call
    term = out["terms"]["x"]
    assert (term["complete"], term["covered_since"]) == (False, "2026-10-21")
    assert (term["calls"], term["waited_s"]) == (9, 70)


def test_a_search_stops_when_its_240_s_of_waiting_are_spent_keeping_what_it_fetched(
    root, capsys, monkeypatch, clock, slept
):
    found = post("a1", "2026-10-01")
    replies = [
        (6.0, slowed(10)),  # a timeout: wait 10 s, halve
        (1.0, data(found)),  # the newest half: one post
        (0.3, slowed(120)),  # the older half, throttled: wait 120 s (130 in all)
        (0.3, slowed(120)),  # again: 120 s more would make 250, past 240: stop
        (0.3, data()),  # the comments
    ]
    seen = wire(monkeypatch, arcticshift, timed(clock, *replies))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    assert main([*argv, *RANGE, "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert asked(seen) == [
        ("posts", "2026-08-01", "2026-10-21"),
        ("posts", "2026-09-10", "2026-10-21"),
        ("posts", "2026-08-01", "2026-09-10"),
        ("posts", "2026-08-01", "2026-09-10"),
        ("comments", "2026-08-01", "2026-10-21"),
    ]
    assert slept == [10, 120]
    term = out["terms"]["x"]
    assert (term["posts"], term["complete"], term["covered_since"]) == (1, False, "2026-09-10")
    assert (term["calls"], term["waited_s"]) == (5, 130)
    [path] = research(root, "reddit_mentions")  # the run went on and wrote what it found
    assert json.loads(path.read_text(encoding="utf-8")) == out


def test_timeouts_halve_down_until_the_calls_are_spent_keeping_what_was_fetched(
    root, capsys, monkeypatch, clock, slept
):
    # Arctic Shift times out (6 s) on more than 10 days; 6 days answer one item each
    made = iter(range(1000))

    def handler(request):
        after = date.fromisoformat(request.url.params["after"])
        before = date.fromisoformat(request.url.params["before"])
        if (before - after).days > 10:
            clock.now += 6.0
            return slowed(5)
        make = post if request.url.path == "/api/posts/search" else comment
        return data(make(f"i{next(made)}", after.isoformat()))

    seen = wire(monkeypatch, arcticshift, handler)
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    assert main([*argv, *RANGE, "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    posts = [(after, before) for kind, after, before in asked(seen) if kind == "posts"]
    assert posts == [
        ("2026-08-01", "2026-10-21"),  # 81 days: a timeout
        ("2026-09-10", "2026-10-21"),  # 41: a timeout
        ("2026-09-30", "2026-10-21"),  # 21: a timeout
        ("2026-10-10", "2026-10-21"),  # 11: a timeout
        ("2026-10-15", "2026-10-21"),  # 6: one post
        ("2026-10-09", "2026-10-15"),
        ("2026-10-03", "2026-10-09"),
        ("2026-09-27", "2026-10-03"),  # the 8th call: the search stops, its posts kept
    ]
    assert len(seen) == 16 and slept == [5] * 8  # the comments search went the same way
    term = out["terms"]["x"]
    assert (term["posts"], term["comments"], term["complete"]) == (4, 4, False)
    assert term["covered_since"] == "2026-09-27"
    assert (term["calls"], term["waited_s"]) == (16, 40)
    assert term["by_month"] == {"2026-09": 2, "2026-10": 6}


def test_a_one_day_window_that_times_out_ends_its_search(root, capsys, monkeypatch, clock, slept):
    replies = [(6.0, slowed(5)), (6.0, slowed(5))]
    seen = wire(monkeypatch, arcticshift, timed(clock, *replies))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    out = run_json(capsys, [*argv, "--since", "2026-10-20", "--until", "2026-10-20"])
    assert asked(seen) == [
        ("posts", "2026-10-20", "2026-10-21"),
        ("comments", "2026-10-20", "2026-10-21"),
    ]
    assert slept == []  # a day cannot be halved: nothing more to ask, nothing to wait for
    term = out["terms"]["x"]
    assert (term["posts"], term["complete"], term["covered_since"]) == (0, False, "2026-10-21")


def test_a_reddit_dry_run_counts_each_fixture_item_once(root, capsys, no_secrets):
    # the fixtures answer every window with the same items: they count once, and the search
    # runs to the start of the range instead of stopping at --limit on repeats
    argv = ["reddit_mentions", "--idea", "_fixture", "--dry-run", "--terms", "x"]
    out = run_json(capsys, [*argv, "--subreddits", "FacebookAds"])
    term = out["terms"]["x"]
    posts = fixture("arcticshift/posts_search")["data"]
    comments = fixture("arcticshift/comments_search")["data"]
    assert (term["posts"], term["comments"]) == (len(posts), len(comments))
    assert term["complete"] is True


def test_reddit_mentions_hits_are_the_newest_limit_items_of_a_term(root, capsys, monkeypatch):
    items = [post(f"p{n}", f"2026-10-{n:02d}") for n in range(1, 5)]
    items += [post(f"q{n}", f"2026-10-{n:02d}", subreddit="PPC") for n in range(5, 9)]
    wire(monkeypatch, arcticshift, arctic(items))
    argv = [
        "reddit_mentions",
        "--idea",
        "_fixture",
        "--terms",
        "x",
        "--subreddits",
        "FacebookAds,PPC",
    ]
    out = run_json(capsys, [*argv, *RANGE, "--limit", "5"])
    hits = out["terms"]["x"]["hits"]
    assert [hit["url"].split("/")[-2] for hit in hits] == ["q8", "q7", "q6", "q5", "p4"]
    assert out["terms"]["x"]["posts"] == 8


def test_reddit_mentions_summary_is_one_row_per_term(root, capsys, monkeypatch):
    wire(monkeypatch, arcticshift, arctic(ITEMS))
    # the fake answers every term alike
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "ad account hacked", "bm hacked"]
    assert main([*argv, "--subreddits", "FacebookAds,PPC", *RANGE]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "term               posts  comments  top subreddits",
        rule(17, 5, 8, 24),
        "ad account hacked  2      2         FacebookAds (3), PPC (1)",
        "bm hacked          2      2         FacebookAds (3), PPC (1)",
    ]


def test_reddit_mentions_summary_names_the_incomplete_terms(root, capsys, monkeypatch):
    full = [raw(post(f"p{n}", "2026-09-15", at=36000 + n * 60)) for n in range(100)]
    wire(monkeypatch, arcticshift, answer({"data": full}))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    assert main([*argv, *RANGE]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == (
        '"x": every match fetched only from 2026-09-16 on, so its counts are lower bounds (a '
        "search came back full, or ran out of calls or waiting time, or was skipped; 2 calls, "
        "0 s waited on Arctic Shift)"
    )


def test_reddit_mentions_summary_says_when_no_day_was_covered(root, capsys, monkeypatch, clock):
    wire(monkeypatch, arcticshift, timed(clock, (6.0, slowed(5)), (6.0, slowed(5))))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    assert main([*argv, "--since", "2026-10-20", "--until", "2026-10-20"]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == (
        '"x": no day fetched in full, so its counts are lower bounds (a search came back full, '
        "or ran out of calls or waiting time, or was skipped; 2 calls, 0 s waited on Arctic "
        "Shift)"
    )


def test_the_run_skips_its_remaining_searches_once_its_wait_budget_is_spent(
    root, capsys, monkeypatch, clock, slept
):
    # three terms in one subreddit: six searches; Arctic Shift throttles the first (4 s resets)
    seen = wire(monkeypatch, arcticshift, timed(clock, *[(0.3, slowed(4))] * 3))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "a", "b", "c"]
    argv += ["--subreddits", "PPC", *RANGE, "--max-wait-s", "10"]
    assert main([*argv, "--json"]) == 0
    out, err = capsys.readouterr()
    data = json.loads(out)
    # the first search waits what it can (4 s, 4 s); a third 4 s would pass 10 s: it stops
    assert asked(seen) == [("posts", "2026-08-01", "2026-10-21")] * 3 and slept == [4, 4]
    assert (data["max_wait_s"], data["waited_s"], data["skipped_searches"]) == (10, 8, 5)
    first, *others = data["terms"].values()
    assert (first["complete"], first["skipped"], first["calls"], first["waited_s"]) == (
        False,
        True,  # its comments search was skipped
        3,
        8,
    )
    for term in others:  # never searched
        assert (term["complete"], term["skipped"], term["calls"], term["waited_s"]) == (
            False,
            True,
            0,
            0,
        )
        assert (term["posts"], term["comments"], term["hits"]) == (0, 0, [])
        assert term["covered_since"] == "2026-10-21"  # no day fetched
    [path] = research(root, "reddit_mentions")
    assert json.loads(path.read_text(encoding="utf-8")) == data


def test_the_summary_says_how_many_searches_were_skipped(root, capsys, monkeypatch, clock):
    wire(monkeypatch, arcticshift, timed(clock, *[(0.3, slowed(4))] * 3))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "a", "b", "c"]
    assert main([*argv, "--subreddits", "PPC", *RANGE, "--max-wait-s", "10"]) == 0
    assert capsys.readouterr().out.splitlines()[-4:] == [
        '"a": no day fetched in full, so its counts are lower bounds (a search came back full, '
        "or ran out of calls or waiting time, or was skipped; 3 calls, 8 s waited on Arctic "
        "Shift)",
        '"b": not searched: the run\'s waiting budget was spent',
        '"c": not searched: the run\'s waiting budget was spent',
        "5 searches skipped: the run waited 8 s on Arctic Shift and --max-wait-s 10 could not "
        "cover another wait",
    ]


def test_the_per_search_budgets_hold_inside_the_run_budget(root, capsys, monkeypatch, clock, slept):
    # a run budget large enough: the posts search stops at its own 8 calls, and the comments
    # search still runs
    replies = [*[(0.3, slowed(1))] * 8, (0.3, data())]
    seen = wire(monkeypatch, arcticshift, timed(clock, *replies))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    out = run_json(capsys, [*argv, *RANGE, "--max-wait-s", "1000"])
    assert len(seen) == 9 and slept == [1] * 7
    assert (out["skipped_searches"], out["terms"]["x"]["skipped"]) == (0, False)


@pytest.mark.parametrize("value", ["-1", "soon", "nan"])
def test_max_wait_s_is_a_number_of_seconds(root, capsys, monkeypatch, value):
    monkeypatch.setattr(arcticshift, "client", lambda dry_run=False: pytest.fail("client built"))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    assert main([*argv, "--max-wait-s", value]) == 2
    assert "is not a number of seconds" in capsys.readouterr().err


def test_a_throttled_selftest_waits_the_reset_once_and_retries(root, capsys, monkeypatch, clock):
    replies = [(0.3, slowed(12)), (0.5, data(post("a", "2026-10-10"), post("b", "2026-10-11")))]
    seen = wire(monkeypatch, arcticshift, timed(clock, *replies))
    slept = []
    monkeypatch.setattr(time, "sleep", slept.append)
    assert main(["reddit_mentions", "--selftest"]) == 0
    assert capsys.readouterr().out == "OK arcticshift 2 items\n"
    assert slept == [12] and len(seen) == 2
    assert seen[0].url == seen[1].url  # the same call, once more


@pytest.mark.parametrize(("reset", "wait"), [(12, 12), (500, 60), (None, 3)])
def test_a_selftest_refused_again_fails_saying_what_it_waited(
    root, capsys, monkeypatch, clock, reset, wait
):
    seen = wire(monkeypatch, arcticshift, timed(clock, (0.3, slowed(reset)), (0.3, slowed(reset))))
    slept = []
    monkeypatch.setattr(time, "sleep", slept.append)
    assert main(["reddit_mentions", "--selftest"]) == 1
    out, err = capsys.readouterr()
    assert out == "" and slept == [wait] and len(seen) == 2
    [line] = err.splitlines()
    assert line.startswith("reddit_mentions: arcticshift: HTTP 422: GET /api/posts/search?")
    assert line.endswith(f"(refused again after waiting {wait} s on a throttle)")


def test_a_selftest_that_times_out_fails_at_once(root, capsys, monkeypatch, clock):
    seen = wire(monkeypatch, arcticshift, timed(clock, (6.0, slowed(5))))
    slept = []
    monkeypatch.setattr(time, "sleep", slept.append)
    assert main(["reddit_mentions", "--selftest"]) == 1
    [line] = capsys.readouterr().err.splitlines()
    assert line.startswith("reddit_mentions: arcticshift: HTTP 422: GET /api/posts/search?")
    assert slept == [] and len(seen) == 1  # a timeout is no throttle: nothing to wait out


def test_reddit_mentions_summary_explains_a_slow_complete_term(root, capsys, monkeypatch, clock):
    replies = [(0.4, slowed(42)), (0.5, data()), (0.5, data())]
    wire(monkeypatch, arcticshift, timed(clock, *replies))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "PPC"]
    assert main([*argv, *RANGE]) == 0
    assert capsys.readouterr().out.splitlines()[-1] == (
        '"x": complete after 3 calls and 42 s waited on Arctic Shift'
    )


@pytest.mark.parametrize(
    ("argv", "needle"),
    [
        (["--terms", "x"], "--subreddits is required"),
        (["--terms", "x", "--subreddits", " , r/ "], "--subreddits is required"),
        (["--subreddits", "PPC"], "no term: give --terms T ..."),
        (["--terms", "x", "--subreddits", "PPC", "--limit", "0"], "is not 1 or more"),
        (
            [
                "--terms",
                "x",
                "--subreddits",
                "PPC",
                "--since",
                "2026-10-21",
                "--until",
                "2026-10-20",
            ],
            "--since 2026-10-21 is after --until 2026-10-20",
        ),
        (
            ["--terms", "x", "--subreddits", "PPC", "--since", "21/10/2026"],
            "not a day as YYYY-MM-DD",
        ),
    ],
)
def test_reddit_mentions_refuses_a_command_line_it_cannot_run(
    root, capsys, monkeypatch, argv, needle
):
    monkeypatch.setattr(arcticshift, "client", lambda dry_run=False: pytest.fail("client built"))
    assert main(["reddit_mentions", "--idea", "_fixture", *argv]) == 2
    assert needle in capsys.readouterr().err


def test_reddit_mentions_stops_on_one_line_when_arctic_shift_refuses(root, capsys, monkeypatch):
    refusal = {"data": None, "error": "Subreddit not found"}
    wire(monkeypatch, arcticshift, answer(refusal, status=400))
    argv = ["reddit_mentions", "--idea", "_fixture", "--terms", "x", "--subreddits", "nope"]
    assert main(argv) == 1
    out, err = capsys.readouterr()
    assert out == "" and err.startswith(
        "reddit_mentions: arcticshift: HTTP 400: GET /api/posts/search?"
    )
    assert "Subreddit not found" in err and err.count("\n") == 1
    assert research(root, "reddit_mentions") == []


# --- hn_mentions -------------------------------------------------------------------------------


STORY = {
    "objectID": "101",
    "created_at_i": ts("2026-10-01") + 60,
    "title": "Ask HN: My ad account was hacked",
    "url": "https://blog.example/hacked",
    "points": 12,
    "num_comments": 4,
    "story_text": '<p>It happened &amp; I lost <a href="https://x.example/a" rel="nofollow">'
    "https://x.example/a</a></p>",
    "author": "user1",
    "_tags": ["story", "author_user1", "story_101"],
}
COMMENT = {
    "objectID": "202",
    "created_at_i": ts("2026-09-15") + 60,
    "comment_text": "Mine too, <i>twice</i>.<p>Use keys&#x27; 2FA.",
    "story_title": "Ask HN: My ad account was hacked",
    "story_id": 101,
    "points": None,
    "author": "user2",
    "_tags": ["comment", "author_user2", "story_101"],
}
OLD_COMMENT = {  # no _tags: the tag asked says what it is
    "objectID": "203",
    "created_at_i": ts("2026-08-20") + 60,
    "comment_text": "Same.",
    "story_title": "Ask HN: My ad account was hacked",
    "story_id": 101,
}


def algolia(stories, comments, nb_stories=None, nb_comments=None):
    """A fake Algolia answering `stories` to tags=story and `comments` to tags=comment, with
    their nbHits (default: as many as given)."""

    def handler(request):
        is_story = request.url.params["tags"] == "story"
        hits = stories if is_story else comments
        nb = nb_stories if is_story else nb_comments
        return httpx.Response(200, json={"hits": hits, "nbHits": len(hits) if nb is None else nb})

    return handler


def test_hn_mentions_asks_stories_then_comments_of_each_term(root, capsys, monkeypatch):
    seen = wire(monkeypatch, algolia_hn, answer({"hits": [], "nbHits": 0}))
    argv = ["hn_mentions", "--idea", "_fixture", "--terms", "ad account hacked", "business manager"]
    assert main([*argv, *RANGE, "--limit", "50"]) == 0
    assert [(r.url.params["query"], r.url.params["tags"]) for r in seen] == [
        ("ad account hacked", "story"),
        ("ad account hacked", "comment"),
        ("business manager", "story"),
        ("business manager", "comment"),
    ]
    # Algolia's bounds are strict: the second before --since, so its first second counts
    since, until = ts("2026-08-01") - 1, ts("2026-10-21")
    assert {r.url.params["numericFilters"] for r in seen} == {
        f"created_at_i>{since},created_at_i<{until}"
    }
    assert {(r.url.params["hitsPerPage"], r.url.params["typoTolerance"]) for r in seen} == {
        ("50", "false")
    }


def test_hn_mentions_counts_the_matches_and_keeps_the_newest_hits(root, capsys, monkeypatch):
    wire(monkeypatch, algolia_hn, algolia([STORY], [COMMENT, OLD_COMMENT], nb_comments=7))
    out = run_json(
        capsys, ["hn_mentions", "--idea", "_fixture", "--terms", "ad account hacked", *RANGE]
    )
    assert out == {
        "since": "2026-08-01",
        "until": "2026-10-20",
        "limit": 100,
        "terms": {
            "ad account hacked": {
                "stories": 1,
                "comments": 7,
                "by_month": {"2026-08": 1, "2026-09": 1, "2026-10": 1},
                "complete": False,
                "hits": [
                    {
                        "kind": "story",
                        "title": "Ask HN: My ad account was hacked",
                        "url": "https://news.ycombinator.com/item?id=101",
                        "score": 12,
                        "created": "2026-10-01",
                        "snippet": "It happened & I lost https://x.example/a",
                    },
                    {
                        "kind": "comment",
                        "title": "Ask HN: My ad account was hacked",
                        "url": "https://news.ycombinator.com/item?id=202",
                        "score": None,
                        "created": "2026-09-15",
                        "snippet": "Mine too, twice. Use keys' 2FA.",
                    },
                    {
                        "kind": "comment",
                        "title": "Ask HN: My ad account was hacked",
                        "url": "https://news.ycombinator.com/item?id=203",
                        "score": None,
                        "created": "2026-08-20",
                        "snippet": "Same.",
                    },
                ],
            }
        },
    }


def test_hn_mentions_hits_are_the_newest_limit_items_each_once(root, capsys, monkeypatch):
    # the dry-run fixture answers both searches: an item both answer is one hit
    stories = [dict(STORY, objectID=str(n), created_at_i=ts(f"2026-10-{n:02d}")) for n in (1, 3)]
    comments = [dict(COMMENT, objectID=str(n), created_at_i=ts(f"2026-10-{n:02d}")) for n in (2, 4)]
    wire(monkeypatch, algolia_hn, algolia(stories, comments + stories[:1]))
    out = run_json(
        capsys, ["hn_mentions", "--idea", "_fixture", "--terms", "x", *RANGE, "--limit", "3"]
    )
    term = out["terms"]["x"]
    assert [hit["url"].rsplit("=", 1)[1] for hit in term["hits"]] == ["4", "3", "2"]
    assert [hit["kind"] for hit in term["hits"]] == ["comment", "story", "comment"]
    assert (term["stories"], term["comments"], term["complete"]) == (2, 3, True)


def test_hn_mentions_skips_a_hit_without_an_id_or_a_sane_time(root, capsys, monkeypatch):
    hits = [STORY, dict(STORY, objectID=None), dict(STORY, objectID="9", created_at_i=1e20)]
    wire(monkeypatch, algolia_hn, algolia(hits, []))
    out = run_json(capsys, ["hn_mentions", "--idea", "_fixture", "--terms", "x", *RANGE])
    assert [hit["url"] for hit in out["terms"]["x"]["hits"]] == [
        "https://news.ycombinator.com/item?id=101"
    ]


def test_hn_mentions_summary_is_one_row_per_term(root, capsys, monkeypatch):
    wire(monkeypatch, algolia_hn, algolia([STORY], [COMMENT, OLD_COMMENT], nb_comments=7))
    argv = ["hn_mentions", "--idea", "_fixture", "--terms", "ad account hacked", *RANGE]
    assert main(argv) == 0
    assert capsys.readouterr().out.splitlines() == [
        "term               stories  comments",
        rule(17, 7, 8),
        "ad account hacked  1        7",
        'not every match fetched (--limit 100): the by_month and hits of "ad account hacked" '
        "cover the newest only",
    ]


@pytest.mark.parametrize(
    ("argv", "needle"),
    [
        ([], "no term: give --terms T ..."),
        (["--terms", "x", "--limit", "1001"], "at most 1000"),
        (["--terms", "x", "--until", "2026-13-01"], "not a day as YYYY-MM-DD"),
    ],
)
def test_hn_mentions_refuses_a_command_line_it_cannot_run(root, capsys, monkeypatch, argv, needle):
    monkeypatch.setattr(algolia_hn, "client", lambda dry_run=False: pytest.fail("client built"))
    assert main(["hn_mentions", "--idea", "_fixture", *argv]) == 2
    assert needle in capsys.readouterr().err


# --- pricing_scan ------------------------------------------------------------------------------


SAAS = """# Stop ad account takeovers

Watchdog for **Meta** and Google ad accounts.

[Log in](https://watch.example/login) [Start free trial](https://watch.example/signup)

## Pricing

| Plan | Price |
| --- | --- |
| Solo | $29/mo |
| Agency | $99/mo |
| Enterprise | Contact sales |

In France: 27 € HT par mois.
"""
ENTERPRISE = """## Enterprise security

Talk to sales for a quote.

[Book a demo](https://enterprise.example/demo)
"""
LIFETIME = "# Lifetime deal\n\nPay once: $199. [Buy now](https://lifetime.example/buy)\n"
PAGES = {
    "https://watch.example/pricing": (SAAS, "Watchdog | Pricing"),
    "https://enterprise.example": (ENTERPRISE, ["Enterprise", "Other title"]),
    "https://lifetime.example/": (LIFETIME, None),
}


def scrapes(pages):
    """A fake Firecrawl answering each URL with its markdown and title from `pages`."""

    def handler(request):
        url = json.loads(request.content)["url"]
        markdown, title = pages[url]
        metadata = {"sourceURL": url, "statusCode": 200}
        if title is not None:
            metadata["title"] = title
        return httpx.Response(
            200, json={"success": True, "data": {"markdown": markdown, "metadata": metadata}}
        )

    return handler


def test_pricing_scan_reads_the_offer_of_each_page(root, capsys, monkeypatch):
    seen = wire(monkeypatch, firecrawl, scrapes(PAGES))
    argv = ["pricing_scan", "--idea", "_fixture", "--urls", "https://watch.example/pricing"]
    out = run_json(capsys, [*argv, "enterprise.example", "https://lifetime.example/"])
    assert out == {
        "pages": [
            {
                "url": "https://watch.example/pricing",
                "title": "Watchdog | Pricing",
                "headline": "Stop ad account takeovers",
                "prices": ["$29/mo", "$99/mo", "27 € HT par mois"],
                "cta": "Start free trial",
                "offer_shape": "subscription",
            },
            {
                "url": "https://enterprise.example",
                "title": "Enterprise",
                "headline": "Enterprise security",
                "prices": [],
                "cta": "Book a demo",
                "offer_shape": "quote",
            },
            {
                "url": "https://lifetime.example/",
                "title": None,
                "headline": "Lifetime deal",
                "prices": ["$199"],
                "cta": "Buy now",
                "offer_shape": "one_shot",
            },
        ]
    }
    assert [json.loads(r.content)["url"] for r in seen] == list(PAGES)


def test_pricing_scan_summary_is_one_row_per_page(root, capsys, monkeypatch):
    wire(monkeypatch, firecrawl, scrapes(PAGES))
    argv = ["pricing_scan", "--idea", "_fixture", "--urls", "https://watch.example/pricing"]
    assert main([*argv, "https://enterprise.example"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "url                            offer_shape   prices                            cta",
        rule(29, 12, 32, 16),
        "https://watch.example/pricing  subscription  $29/mo, $99/mo, 27 € HT par mois  "
        "Start free trial",
        "https://enterprise.example     quote                                           "
        "Book a demo",
    ]


def test_pricing_scan_logs_one_firecrawl_call_per_page(root, monkeypatch):
    wire(monkeypatch, firecrawl, scrapes(PAGES))
    before = costs.total("_fixture", kind="api")
    argv = ["pricing_scan", "--idea", "_fixture", "--urls", "https://watch.example/pricing"]
    assert main([*argv, "https://enterprise.example"]) == 0
    assert costs.total("_fixture", kind="api") == round(before + 0.02, 4)
    line = costs.read_lines("_fixture")[-1]
    [path] = research(root, "pricing_scan")
    assert {k: line[k] for k in ("kind", "provider", "amount_eur", "ref", "phase", "note")} == {
        "kind": "api",
        "provider": "firecrawl",
        "amount_eur": 0.02,
        "ref": path.name,
        "phase": "triage",
        "note": "2 firecrawl calls at 0.01 EUR",
    }


def test_pricing_scan_bills_only_the_scrapes_answered_before_a_failure(root, capsys, monkeypatch):
    ok = scrapes(PAGES)
    replies = iter([ok, *[lambda request: httpx.Response(500, text="boom")] * 3])
    wire(monkeypatch, firecrawl, lambda request: next(replies)(request))
    before = costs.total("_fixture", kind="api")
    argv = ["pricing_scan", "--idea", "_fixture", "--urls", "https://watch.example/pricing"]
    assert main([*argv, "https://enterprise.example"]) == 1
    assert research(root, "pricing_scan") == []
    # two scrapes asked: the first answered (billed), the second refused after its retries
    assert costs.total("_fixture", kind="api") == round(before + 0.01, 4)
    err = capsys.readouterr().err.splitlines()
    assert (
        err[0] == "pricing_scan: 0.01 EUR (1 firecrawl call at 0.01 EUR) logged before the failure"
    )
    assert (
        err[1].startswith("pricing_scan: firecrawl: HTTP 500: POST /v1/scrape: ") and len(err) == 2
    )


@pytest.mark.parametrize("status", [500, 402])
def test_a_scrape_firecrawl_refuses_is_not_billed(root, capsys, monkeypatch, status):
    wire(monkeypatch, firecrawl, answer({"success": False, "error": "refused"}, status=status))
    log = root / "ideas/_fixture/costs.jsonl"
    before = log.read_text(encoding="utf-8")
    assert main(["pricing_scan", "--idea", "_fixture", "--urls", "https://example.com"]) == 1
    assert log.read_text(encoding="utf-8") == before  # no cost line
    assert research(root, "pricing_scan") == []
    [err] = capsys.readouterr().err.splitlines()
    assert err.startswith(f"pricing_scan: firecrawl: HTTP {status}: POST /v1/scrape: ")


def test_pricing_scan_plans_one_scrape_per_page_against_the_cap(root, capsys):
    # the fixture idea has spent 0.40 EUR: a cap of 0.42 leaves room for two scrapes, not three
    assert main(["idea", "set", "_fixture", "cap_eur=0.42"]) == 0
    argv = ["pricing_scan", "--idea", "_fixture", "--dry-run", "--urls", "a.example", "b.example"]
    assert main(argv) == 0
    capsys.readouterr()
    assert main([*argv, "c.example"]) == 1
    assert "over its cap of 0.42 EUR" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("argv", "needle"),
    [
        ([], "no URL: give --urls U ..."),
        (["--urls", "not a url"], "not a web page address: 'not a url'"),
        (["--urls", "ftp://files.example/x"], "not a web page address: 'ftp://files.example/x'"),
    ],
)
def test_pricing_scan_refuses_what_is_not_a_web_page(root, capsys, monkeypatch, argv, needle):
    monkeypatch.setattr(firecrawl, "client", lambda dry_run=False: pytest.fail("client built"))
    assert main(["pricing_scan", "--idea", "_fixture", *argv]) == 2
    assert needle in capsys.readouterr().err


def test_pricing_scan_asks_each_page_once(root, capsys, monkeypatch):
    seen = wire(monkeypatch, firecrawl, scrapes(PAGES))
    argv = ["pricing_scan", "--idea", "_fixture", "--urls", "enterprise.example"]
    out = run_json(capsys, [*argv, "https://enterprise.example", " enterprise.example "])
    assert len(seen) == 1 and [page["url"] for page in out["pages"]] == [
        "https://enterprise.example"
    ]


# --- domain_check ------------------------------------------------------------------------------


STATUSES = {
    "meikit.com": 200,
    "meikit.io": "none",
    "meikit.ai": 200,
    "meikit.dev": 404,
    "meikit.fr": 404,
}


def test_domain_check_asks_each_tld_and_names_the_lab_address(root, capsys, monkeypatch):
    seen = wire(monkeypatch, rdap, rdap_org(STATUSES))
    out = run_json(capsys, ["domain_check", "--idea", "_fixture", "--name", " Meikit "])
    assert out == {
        "name": "meikit",
        "domains": {
            "meikit.com": "taken",
            "meikit.io": "unknown",
            "meikit.ai": "taken",
            "meikit.dev": "available",
            "meikit.fr": "available",
        },
        "lab": "meikit.meikit.ai",
    }
    asked = [r.url.path for r in seen if r.url.host == "rdap.org"]
    assert asked == [f"/domain/{domain}" for domain in STATUSES]


def test_domain_check_summary_is_one_row_per_domain_then_the_lab(root, capsys, monkeypatch):
    wire(monkeypatch, rdap, rdap_org(STATUSES))
    assert (
        main(["domain_check", "--idea", "_fixture", "--name", "meikit", "--tlds", ".IO, dev,,io"])
        == 0
    )
    assert capsys.readouterr().out.splitlines() == [
        "domain      status",
        rule(10, 9),
        "meikit.io   unknown",
        "meikit.dev  available",
        "lab: meikit.meikit.ai",
    ]


@pytest.mark.parametrize(
    ("argv", "needle"),
    [
        ([], "--name is required"),
        (["--name", "ad watch"], "not a domain name label: 'ad watch'"),
        (["--name", "meikit.ai"], "not a domain name label: 'meikit.ai'"),
        (["--name=meikit-"], "not a domain name label: 'meikit-'"),
        (["--name", "meikit", "--tlds", " , "], "no TLD: give --tlds com,io,..."),
        (["--name", "meikit", "--tlds", "com,c_m"], "not a TLD: 'c_m'"),
    ],
)
def test_domain_check_refuses_a_name_or_tld_it_cannot_ask(root, capsys, monkeypatch, argv, needle):
    monkeypatch.setattr(rdap, "client", lambda dry_run=False: pytest.fail("client built"))
    assert main(["domain_check", "--idea", "_fixture", *argv]) == 2
    assert needle in capsys.readouterr().err
