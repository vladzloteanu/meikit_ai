import json
import time

import httpx
import pytest

from factory import costs, secrets
from factory.cli import main
from factory.http import FIXTURES, Client, ProviderError
from factory.providers import searchapi, seranking
from factory.secrets import SecretsUnavailable

QUOTA = "You have used all of the searches for the month. Please upgrade your plan."
ITEM_KEYS = [
    "advertiser",
    "page_or_domain",
    "text",
    "format",
    "first_seen",
    "last_seen",
    "active",
    "link",
]
# One argv per tool and engine that a dry run can answer from the fixtures.
DRY_RUNS = [
    ["serp_ads", "--keywords", "facebook ad account hacked"],
    ["keyword_volume", "--cc", "us", "--keywords", "facebook ad account hacked"],
    ["ad_library", "--engine", "meta", "--q", "ad account security"],
    ["ad_library", "--engine", "tiktok", "--q", "ad account hacked"],
    ["ad_library", "--engine", "linkedin", "--q", "ad account security"],
    ["ad_library", "--engine", "google_transparency", "--domain", "hootsuite.com"],
]
DRY_RUN_IDS = ["serp_ads", "keyword_volume", "meta", "tiktok", "linkedin", "google_transparency"]

# SE Ranking rows shaped like its documented answer: one with data, one without (the fixture's).
FOUND = {
    "is_data_found": True,
    "keyword": "business manager hacked",
    "volume": 320,
    "cpc": 2.5,
    "competition": 0.12,
    "difficulty": 18,
    "intents": ["I"],
    "history_trend": {
        "2026-10-01": 390,
        "2025-11-01": 210,
        "2026-01-01": 260,
        "2025-12-01": 240,
        "2026-02-01": 250,
        "2026-03-01": 300,
        "2026-04-01": 320,
        "2026-05-01": 330,
        "2026-06-01": 310,
        "2026-07-01": 350,
        "2026-08-01": 360,
        "2026-09-01": 380,
    },
}
FOUND_TREND = [210, 240, 260, 250, 300, 320, 330, 310, 350, 360, 380, 390]
NOT_FOUND = {"keyword": "facebook ad account hacked", "is_data_found": False}
NO_DATA = {
    "volume": None,
    "cpc": None,
    "competition": None,
    "difficulty": None,
    "intents": [],
    "trend_12m": [],
    "found": False,
}


def research(root, tool):
    return sorted((root / "ideas/_fixture/research").glob(f"{tool}_*"))


def fixture(name):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def mock_client(provider, reply, seen=None, **options):
    """A real Client for `provider` whose transport answers each request with `reply(request)`."""

    def handler(request):
        if seen is not None:
            seen.append(request)
        return reply(request)

    return Client(provider, "https://x.test", transport=httpx.MockTransport(handler), **options)


def answer(data, status=200):
    return lambda request: httpx.Response(status, json=data)


def wire(monkeypatch, module, reply, seen=None, **options):
    """Make `module.client()` a mock client answering `reply`."""
    provider = module.__name__.rsplit(".", 1)[-1]
    monkeypatch.setattr(
        module, "client", lambda dry_run=False: mock_client(provider, reply, seen, **options)
    )


def buckets_file(tmp_path, buckets):
    path = tmp_path / "buckets.json"
    path.write_text(json.dumps(buckets), encoding="utf-8")
    return str(path)


def run_json(capsys, argv):
    """Run `argv` with --json; its exit code must be 0. The research JSON it printed."""
    assert main([*argv, "--json"]) == 0
    return json.loads(capsys.readouterr().out)


# --- the brief's tests -------------------------------------------------------------------------


def test_dry_run_needs_no_secrets(root, capsys, monkeypatch):
    monkeypatch.setattr(
        secrets, "load", lambda *a, **k: (_ for _ in ()).throw(SecretsUnavailable("no key"))
    )
    assert (
        main(["keyword_volume", "--idea", "_fixture", "--dry-run", "--cc", "us", "--keywords", "x"])
        == 0
    )
    assert list((root / "ideas/_fixture/research").glob("keyword_volume_*.json"))


def test_unknown_idea_refused(root, capsys):
    assert main(["serp_ads", "--idea", "nope", "--dry-run", "--keywords", "x"]) == 1
    assert "ideas/" in capsys.readouterr().err


def test_output_written_atomically(root, monkeypatch):
    # make the provider raise after the client call: no *.json must remain, and no .tmp either
    monkeypatch.setattr(
        searchapi,
        "search",
        lambda *a, **k: (_ for _ in ()).throw(ProviderError("searchapi", 500, "x")),
    )
    assert main(["serp_ads", "--idea", "_fixture", "--keywords", "x", "--dry-run"]) == 1
    assert not list((root / "ideas/_fixture/research").glob("serp_ads_*"))


def test_keyword_volume_buckets(root, tmp_path, capsys):
    f = tmp_path / "b.json"
    f.write_text(
        json.dumps(
            {
                "trigger": ["facebook ad account hacked"],
                "solution_aware": ["business manager hacked"],
            }
        )
    )
    main(
        ["keyword_volume", "--idea", "_fixture", "--dry-run", "--cc", "us"]
        + ["--buckets-file", str(f), "--json"]
    )
    out = json.loads(capsys.readouterr().out)
    assert set(out["buckets"]) == {"trigger", "solution_aware"}


def test_cost_logged_outside_dry_run(root, monkeypatch):
    wire(monkeypatch, searchapi, answer(fixture("searchapi/google")))
    before = costs.total("_fixture", kind="api")  # the fixture idea already holds 0.12 EUR of api
    assert main(["serp_ads", "--idea", "_fixture", "--keywords", "a", "--keywords", "b"]) == 0
    assert costs.total("_fixture", kind="api") >= 0.02
    assert costs.total("_fixture", kind="api") == round(before + 0.02, 4)


# --- every tool --------------------------------------------------------------------------------


def test_the_demand_tools_are_registered(capsys):
    assert main(["--help"]) == 0
    out = capsys.readouterr().out
    assert "serp_ads" in out and "keyword_volume" in out and "ad_library" in out


@pytest.mark.parametrize("argv", DRY_RUNS, ids=DRY_RUN_IDS)
def test_a_dry_run_writes_research_reads_no_key_and_logs_nothing(root, capsys, monkeypatch, argv):
    monkeypatch.setattr(secrets, "get", lambda *a, **k: pytest.fail("a dry run read a secret"))
    log = root / "ideas/_fixture/costs.jsonl"
    before = log.read_text(encoding="utf-8")
    assert main([*argv, "--idea", "_fixture", "--dry-run"]) == 0
    [path] = research(root, argv[0])
    assert path.suffix == ".json" and json.loads(path.read_text(encoding="utf-8"))
    assert log.read_text(encoding="utf-8") == before
    out, err = capsys.readouterr()
    assert out.strip()
    report = err.splitlines()[-1]  # keyword_volume warns first about the fixture's other row
    assert report.startswith(f"{argv[0]}: dry run: wrote ideas/_fixture/research/{argv[0]}_")
    assert report.endswith("not logged")


@pytest.mark.parametrize("argv", DRY_RUNS, ids=DRY_RUN_IDS)
def test_an_unknown_idea_is_refused_before_any_key_or_call(root, capsys, monkeypatch, argv):
    for module in (searchapi, seranking):
        monkeypatch.setattr(module, "client", lambda dry_run=False: pytest.fail("client built"))
    assert main([*argv, "--idea", "nope"]) == 1
    err = capsys.readouterr().err
    assert err.startswith(f"{argv[0]}: no idea 'nope' in ideas/") and err.count("\n") == 1


@pytest.mark.parametrize("argv", DRY_RUNS, ids=DRY_RUN_IDS)
def test_a_real_run_without_the_master_key_stops_on_one_line(root, capsys, argv):
    assert main([*argv, "--idea", "_fixture"]) == 1
    out, err = capsys.readouterr()
    assert out == "" and "make secrets-init" in err and err.count("\n") == 1
    assert research(root, argv[0]) == []


@pytest.mark.parametrize(
    ("argv", "line"),
    [
        (["serp_ads"], "OK searchapi 9 items"),  # the google fixture: 3 ads, 6 organic results
        (["keyword_volume"], "OK seranking 2 items"),
        (["ad_library"], "OK searchapi 4 items"),
    ],
)
def test_a_selftest_dry_run_answers_from_the_fixtures(root, capsys, argv, line):
    assert main([*argv, "--selftest", "--dry-run"]) == 0
    assert capsys.readouterr().out == f"{line}\n"


@pytest.mark.parametrize(
    ("tool", "module", "reply", "line", "request_line"),
    [
        (
            "serp_ads",
            searchapi,
            answer(fixture("searchapi/google")),
            "OK searchapi 9 items",
            "GET /search?engine=google&q=ad+account+security&gl=us&hl=en&num=10",
        ),
        (
            "keyword_volume",
            seranking,
            answer([FOUND], status=201),
            "OK seranking 1 items",
            "POST /research/us/analyze-keywords/",
        ),
        (
            "ad_library",
            searchapi,
            answer(fixture("searchapi/meta_ad_library")),
            "OK searchapi 4 items",
            "GET /search?engine=meta_ad_library&q=ad+account",
        ),
    ],
)
def test_a_selftest_is_one_call_that_writes_and_logs_nothing(
    root, capsys, monkeypatch, tool, module, reply, line, request_line
):
    seen = []
    wire(monkeypatch, module, reply, seen)
    log = root / "ideas/_fixture/costs.jsonl"
    before = log.read_text(encoding="utf-8")
    assert main([tool, "--selftest"]) == 0
    assert capsys.readouterr().out == f"{line}\n"
    assert [f"{r.method} {r.url.raw_path.decode()}" for r in seen] == [request_line]
    assert research(root, tool) == [] and log.read_text(encoding="utf-8") == before


@pytest.mark.parametrize("tool", ["serp_ads", "ad_library"])
def test_a_selftest_stopped_by_the_searchapi_quota_is_one_line(root, capsys, monkeypatch, tool):
    wire(monkeypatch, searchapi, answer({"error": QUOTA}, 429), fatal=searchapi.quota_used_up)
    assert main([tool, "--selftest"]) == 1
    out, err = capsys.readouterr()
    assert out == ""
    assert err.startswith(f"{tool}: searchapi: HTTP 429: GET /search?")
    assert "used all of the searches for the month" in err and err.count("\n") == 1


# --- serp_ads ----------------------------------------------------------------------------------


def test_serp_ads_research_from_the_google_answer(root, capsys):
    out = run_json(
        capsys,
        ["serp_ads", "--idea", "_fixture", "--dry-run"]
        + ["--keywords", "facebook ad account hacked", "ad account security"],
    )
    assert list(out) == ["gl", "hl", "queries", "advertisers"]
    assert (out["gl"], out["hl"]) == ("us", "en")
    assert list(out["queries"]) == ["facebook ad account hacked", "ad account security"]
    serp = out["queries"]["facebook ad account hacked"]
    assert list(serp) == ["n_ads", "ads", "organic"]
    assert serp["n_ads"] == 3 and len(serp["organic"]) == 6
    assert serp["ads"][0] == {
        "position": 1,
        "title": "Hacked Ad Account? - Stop Unauthorized Ad Spend Today",
        "domain": "brindlewick-recovery.example",
        "link": "https://www.brindlewick-recovery.example/hacked-ad-account",
        "snippet": "Lock down your Business Manager, remove unknown admins and file the appeal in "
        "one call. Specialists available 7 days a week.",
        "sitelinks": [
            {
                "title": "Disabled Ad Account Appeals",
                "snippet": "Prepare a clear appeal for a disabled or restricted ad account.",
                "link": "https://www.brindlewick-recovery.example/appeals",
            },
            {
                "title": "Free Account Security Check",
                "snippet": "A 10-point review of admins, payment methods and login alerts.",
                "link": "https://www.brindlewick-recovery.example/security-check",
            },
        ],
    }
    assert serp["ads"][2]["sitelinks"] == []
    assert serp["organic"][0] == {
        "p": 1,
        "domain": "help.adplatform.example",
        "title": "Recover a hacked ad account | Business Help Center",
        "url": "https://help.adplatform.example/business/help/recover-hacked-ad-account",
    }
    # the fixture answers both keywords, so each advertiser is on two of them
    assert out["advertisers"] == {
        "brindlewick-recovery.example": 2,
        "kestrelmark.example": 2,
        "pellucidcare.example": 2,
    }
    [path] = research(root, "serp_ads")
    assert json.loads(path.read_text(encoding="utf-8")) == out


def test_serp_ads_advertisers_run_from_the_most_keywords(root, capsys, monkeypatch):
    serps = {
        "a": {
            "ads": [{"domain": "www.b.example"}, {"domain": "b.example"}, {"domain": "c.example"}]
        },
        "b": {"ads": [{"domain": "c.example"}]},
        "c": {"ads": [{"domain": "a.example"}]},
    }
    wire(
        monkeypatch,
        searchapi,
        lambda request: httpx.Response(200, json=serps[request.url.params["q"]]),
    )
    out = run_json(capsys, ["serp_ads", "--idea", "_fixture", "--keywords", "a", "b", "c"])
    assert list(out["advertisers"].items()) == [
        ("c.example", 2),
        ("a.example", 1),
        ("b.example", 1),
    ]
    assert out["queries"]["a"]["n_ads"] == 3  # two ads of one advertiser are two ads


def test_serp_ads_sends_one_google_search_per_keyword(root, capsys, monkeypatch):
    seen = []
    wire(monkeypatch, searchapi, answer({}), seen)
    argv = ["serp_ads", "--idea", "_fixture", "--keywords", "a b", "--keywords", "c"]
    assert main([*argv, "--gl", "fr", "--hl", "fr", "--num", "20"]) == 0
    assert [dict(r.url.params) for r in seen] == [
        {"engine": "google", "q": "a b", "gl": "fr", "hl": "fr", "num": "20"},
        {"engine": "google", "q": "c", "gl": "fr", "hl": "fr", "num": "20"},
    ]


def test_serp_ads_reads_a_sparse_answer_without_failing(root, capsys, monkeypatch):
    sparse = {
        "ads": [
            {"title": "only a title"},
            "not an ad",
            {
                "link": "https://www.shop.example/x",
                "sitelinks": {"inline": [{"title": "Pricing", "link": "https://shop.example/p"}]},
            },
        ],
        "organic_results": [{"link": "https://blog.example/post"}],
    }
    wire(monkeypatch, searchapi, answer(sparse))
    out = run_json(capsys, ["serp_ads", "--idea", "_fixture", "--keywords", "x"])
    serp = out["queries"]["x"]
    assert serp["ads"] == [
        {
            "position": None,
            "title": "only a title",
            "domain": None,
            "link": None,
            "snippet": None,
            "sitelinks": [],
        },
        {
            "position": None,
            "title": None,
            "domain": "shop.example",
            "link": "https://www.shop.example/x",
            "snippet": None,
            "sitelinks": [{"title": "Pricing", "snippet": None, "link": "https://shop.example/p"}],
        },
    ]
    assert serp["n_ads"] == 2
    assert serp["organic"] == [
        {"p": None, "domain": "blog.example", "title": None, "url": "https://blog.example/post"}
    ]
    assert out["advertisers"] == {"shop.example": 1}


def test_serp_ads_summary_is_one_row_per_keyword(root, capsys):
    argv = [
        "serp_ads",
        "--idea",
        "_fixture",
        "--dry-run",
        "--keywords",
        "facebook ad account hacked",
    ]
    assert main(argv) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].split() == ["keyword", "n_ads", "advertisers"]
    assert lines[2].split() == [
        "facebook",
        "ad",
        "account",
        "hacked",
        "3",
        "brindlewick-recovery.example,",
        "kestrelmark.example,",
        "pellucidcare.example",
    ]
    assert len(lines) == 3


def test_serp_ads_reads_a_keywords_file(root, tmp_path, monkeypatch):
    path = tmp_path / "keywords.txt"
    path.write_text(
        "# triage keywords\nad account hacked\n\n  Ad Account  Hacked \nbusiness manager hacked\n",
        encoding="utf-8",
    )
    seen = []
    wire(monkeypatch, searchapi, answer({}), seen)
    assert main(["serp_ads", "--idea", "_fixture", "--keywords-file", str(path)]) == 0
    assert [r.url.params["q"] for r in seen] == ["ad account hacked", "business manager hacked"]


@pytest.mark.parametrize(
    ("argv", "needle"),
    [
        (["--idea", "_fixture"], "--keywords"),
        (["--idea", "_fixture", "--keywords", " "], "--keywords"),
        (
            ["--idea", "_fixture", "--keywords-file", "/no/such/keywords.txt"],
            "/no/such/keywords.txt",
        ),
        (["--keywords", "x"], "--idea is required"),
    ],
)
def test_serp_ads_refuses_a_command_line_it_cannot_run(root, capsys, argv, needle):
    assert main(["serp_ads", "--dry-run", *argv]) == 2
    err = capsys.readouterr().err
    assert needle in err and err.count("\n") == 1


def test_serp_ads_takes_keywords_or_a_file_not_both(root, tmp_path, capsys):
    path = tmp_path / "k.txt"
    path.write_text("a\n", encoding="utf-8")
    argv = ["serp_ads", "--idea", "_fixture", "--keywords", "b", "--keywords-file", str(path)]
    assert main(argv) == 2
    assert "not allowed with argument" in capsys.readouterr().err


def test_serp_ads_plans_one_search_per_keyword_against_the_cap(root, capsys):
    # the fixture idea has spent 0.40 EUR: a cap of 0.42 leaves room for two searches, not three
    assert main(["idea", "set", "_fixture", "cap_eur=0.42"]) == 0
    assert main(["serp_ads", "--idea", "_fixture", "--dry-run", "--keywords", "a", "b"]) == 0
    capsys.readouterr()
    assert main(["serp_ads", "--idea", "_fixture", "--dry-run", "--keywords", "a", "b", "c"]) == 1
    assert "over its cap of 0.42 EUR" in capsys.readouterr().err


def test_serp_ads_logs_its_searches_with_the_research_file(root, monkeypatch):
    wire(monkeypatch, searchapi, answer(fixture("searchapi/google")))
    before = costs.total("_fixture", kind="api")
    assert main(["serp_ads", "--idea", "_fixture", "--keywords", "a", "--keywords", "b"]) == 0
    assert costs.total("_fixture", kind="api") == round(before + 0.02, 4)
    line = costs.read_lines("_fixture")[-1]
    [path] = research(root, "serp_ads")
    assert {k: line[k] for k in ("kind", "provider", "amount_eur", "ref", "phase", "note")} == {
        "kind": "api",
        "provider": "searchapi",
        "amount_eur": 0.02,
        "ref": path.name,
        "phase": "triage",
        "note": "2 searchapi calls at 0.01 EUR",
    }


def test_serp_ads_logs_the_searches_made_before_a_failure(root, capsys, monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    replies = iter([httpx.Response(200, json={}), *[httpx.Response(500, text="boom")] * 3])
    wire(monkeypatch, searchapi, lambda request: next(replies))
    before = costs.total("_fixture", kind="api")
    assert main(["serp_ads", "--idea", "_fixture", "--keywords", "a", "b"]) == 1
    assert research(root, "serp_ads") == []
    # two searches were made: the first answered, the second failed after its retries
    assert costs.total("_fixture", kind="api") == round(before + 0.02, 4)
    err = capsys.readouterr().err.splitlines()
    assert err[0] == "serp_ads: 0.02 EUR (2 searchapi calls at 0.01 EUR) logged before the failure"
    assert err[1].startswith("serp_ads: searchapi: HTTP 500: GET /search?") and len(err) == 2


# --- keyword_volume ----------------------------------------------------------------------------


def test_keyword_volume_keeps_a_keyword_without_data_as_not_found(
    root, tmp_path, capsys, monkeypatch
):
    monkeypatch.setattr(
        seranking, "analyze_keywords", lambda client, cc, keywords: [FOUND, NOT_FOUND]
    )
    f = buckets_file(
        tmp_path, {"trigger": ["facebook ad account hacked", "business manager hacked"]}
    )
    out = run_json(
        capsys,
        ["keyword_volume", "--idea", "_fixture", "--dry-run", "--cc", "us", "--buckets-file", f],
    )
    assert list(out) == ["cc", "language", "keywords", "buckets"]
    assert (out["cc"], out["language"]) == ("us", "en")
    assert out["keywords"] == {
        "facebook ad account hacked": {**NO_DATA, "bucket": "trigger"},
        "business manager hacked": {
            "volume": 320,
            "cpc": 2.5,
            "competition": 0.12,
            "difficulty": 18,
            "intents": ["I"],
            "trend_12m": FOUND_TREND,
            "found": True,
            "bucket": "trigger",
        },
    }
    assert list(out["keywords"]["business manager hacked"]) == [*NO_DATA, "bucket"]
    assert out["buckets"] == {"trigger": {"volume_sum": 320, "n": 1, "cpc_median": 2.5}}


def test_keyword_volume_bucket_figures_count_only_found_keywords(
    root, tmp_path, capsys, monkeypatch
):
    def row(keyword, volume, cpc):
        return {"keyword": keyword, "is_data_found": True, "volume": volume, "cpc": cpc}

    rows = [row("a", 100, 1.0), row("b", 200, 4.0), row("c", 300, 2.0), row("d", 50, 3.0)]
    rows.append({"keyword": "e", "is_data_found": False})
    monkeypatch.setattr(seranking, "analyze_keywords", lambda client, cc, keywords: rows)
    f = buckets_file(
        tmp_path,
        {
            "adjacent_budget": [],
            "trigger": ["e"],
            "solution_aware": ["a", "b", "c", "d", "missing"],
        },
    )
    out = run_json(
        capsys,
        ["keyword_volume", "--idea", "_fixture", "--dry-run", "--cc", "us", "--buckets-file", f],
    )
    # the buckets in their documented order; an empty one is listed, not dropped
    assert out["buckets"] == {
        "solution_aware": {"volume_sum": 650, "n": 4, "cpc_median": 2.5},
        "trigger": {"volume_sum": 0, "n": 0, "cpc_median": None},
        "adjacent_budget": {"volume_sum": 0, "n": 0, "cpc_median": None},
    }
    assert out["keywords"]["missing"] == {**NO_DATA, "bucket": "solution_aware"}
    assert list(out["keywords"]) == ["a", "b", "c", "d", "missing", "e"]


def test_keyword_volume_summary_is_buckets_then_the_top_keywords(
    root, tmp_path, capsys, monkeypatch
):
    rows = [
        {"keyword": f"kw{i:02d}", "is_data_found": True, "volume": 100 + i, "cpc": 1.0}
        for i in range(20)
    ]
    monkeypatch.setattr(seranking, "analyze_keywords", lambda client, cc, keywords: rows)
    keywords = [f"kw{i:02d}" for i in range(20)]
    f = buckets_file(tmp_path, {"trigger": keywords, "problem_aware": ["never seen"]})
    argv = ["keyword_volume", "--idea", "_fixture", "--dry-run", "--cc", "us", "--buckets-file", f]
    assert main(argv) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].split() == ["bucket", "found", "volume_sum", "cpc_median"]
    assert lines[2].split() == ["problem_aware", "0/1", "0"]
    assert lines[3].split() == ["trigger", "20/20", "2190", "1.0"]
    top = lines.index("top 15 keywords by volume:")
    assert lines[top + 1].split() == [
        "keyword",
        "bucket",
        "volume",
        "cpc",
        "competition",
        "difficulty",
    ]
    assert [line.split()[0] for line in lines[top + 3 : top + 18]] == [
        f"kw{i:02d}" for i in range(19, 4, -1)
    ]
    assert lines[-1] == "no data in SE Ranking (us) for 1 of 21 keywords: never seen"


def test_keyword_volume_without_buckets(root, capsys, monkeypatch):
    seen = {}

    def analyze(client, cc, keywords):
        seen.update(cc=cc, keywords=keywords)
        return [{**FOUND, "keyword": "Business  Manager hacked"}]

    monkeypatch.setattr(seranking, "analyze_keywords", analyze)
    argv = ["keyword_volume", "--idea", "_fixture", "--dry-run", "--cc", "GB", "--language", "fr"]
    out = run_json(
        capsys, [*argv, "--keywords", "business manager hacked", "Business manager HACKED", "x"]
    )
    assert seen == {"cc": "uk", "keywords": ["business manager hacked", "x"]}
    assert (out["cc"], out["language"]) == ("uk", "fr")
    assert out["keywords"]["business manager hacked"]["found"] is True  # matched whatever the case
    assert out["keywords"]["business manager hacked"]["bucket"] is None
    assert out["keywords"]["x"] == {**NO_DATA, "bucket": None}
    assert out["buckets"] == {}


def test_keyword_volume_summary_without_buckets_or_data(root, capsys, monkeypatch):
    monkeypatch.setattr(seranking, "analyze_keywords", lambda client, cc, keywords: [FOUND])
    argv = ["keyword_volume", "--idea", "_fixture", "--dry-run", "--cc", "fr", "--keywords"]
    assert main([*argv, "business manager hacked", "x"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "top 15 keywords by volume:"  # no bucket table, no bucket column
    assert lines[1].split() == ["keyword", "volume", "cpc", "competition", "difficulty"]
    assert lines[3].split() == ["business", "manager", "hacked", "320", "2.5", "0.12", "18"]
    assert lines[4:] == ["", "no data in SE Ranking (fr) for 1 of 2 keywords: x"]
    monkeypatch.setattr(seranking, "analyze_keywords", lambda client, cc, keywords: [])
    assert main([*argv, "x"]) == 0
    assert capsys.readouterr().out == "no data in SE Ranking (fr) for 1 of 1 keywords: x\n"


def test_keyword_volume_warns_about_rows_for_keywords_not_asked(root, capsys):
    # the dry-run fixture answers for its own two keywords, whatever is asked
    argv = ["keyword_volume", "--idea", "_fixture", "--dry-run", "--cc", "us", "--keywords", "x"]
    assert main([*argv, "--json"]) == 0
    out, err = capsys.readouterr()
    assert json.loads(out)["keywords"] == {"x": {**NO_DATA, "bucket": None}}
    assert (
        "keyword_volume: SE Ranking answered for 2 keywords not asked, ignored: "
        "'facebook ad account hacked', 'business manager hacked'"
    ) in err


def test_keyword_volume_pays_one_call_per_20_keywords(root, capsys, monkeypatch):
    seen = []

    def reply(request):
        asked = json.loads(request.content)["keywords"]
        return httpx.Response(201, json=[{"keyword": k, "is_data_found": False} for k in asked])

    wire(monkeypatch, seranking, reply, seen)
    before = costs.total("_fixture", kind="api")
    keywords = [f"kw{i}" for i in range(25)]
    assert (
        main(["keyword_volume", "--idea", "_fixture", "--cc", "us", "--keywords", *keywords]) == 0
    )
    assert [len(json.loads(r.content)["keywords"]) for r in seen] == [20, 5]
    assert costs.total("_fixture", kind="api") == round(before + 0.04, 4)
    line = costs.read_lines("_fixture")[-1]
    assert (line["provider"], line["note"]) == ("seranking", "2 seranking calls at 0.02 EUR")


def test_keyword_volume_plans_one_call_per_20_keywords_against_the_cap(root, capsys):
    assert main(["idea", "set", "_fixture", "cap_eur=0.42"]) == 0
    argv = ["keyword_volume", "--idea", "_fixture", "--dry-run", "--cc", "us", "--keywords"]
    assert main([*argv, *[f"kw{i}" for i in range(20)]]) == 0
    capsys.readouterr()
    assert main([*argv, *[f"kw{i}" for i in range(21)]]) == 1
    assert "over its cap of 0.42 EUR" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("content", "needle"),
    [
        ("not json", "is not valid JSON"),
        ('["a"]', "must hold a JSON object"),
        ('{"triger": ["a"]}', "unknown bucket 'triger'"),
        ('{"trigger": "a"}', "trigger must be a list of keywords"),
        ('{"trigger": ["a", 1]}', "trigger must be a list of keywords"),
        ('{"trigger": ["a"], "problem_aware": ["A "]}', "'a' is in both problem_aware and trigger"),
        ('{"trigger": []}', "holds no keyword"),
    ],
)
def test_keyword_volume_refuses_a_bad_buckets_file(root, tmp_path, capsys, content, needle):
    path = tmp_path / "buckets.json"
    path.write_text(content, encoding="utf-8")
    argv = ["keyword_volume", "--idea", "_fixture", "--dry-run", "--cc", "us"]
    assert main([*argv, "--buckets-file", str(path)]) == 2
    err = capsys.readouterr().err
    assert needle in err and str(path) in err and err.count("\n") == 1


@pytest.mark.parametrize(
    ("argv", "needle"),
    [
        (["--cc", "us"], "--keywords"),
        (["--keywords", "a"], "--cc is required"),
        (["--cc", "us", "--buckets-file", "/no/such/buckets.json"], "/no/such/buckets.json"),
    ],
)
def test_keyword_volume_refuses_a_command_line_it_cannot_run(root, capsys, argv, needle):
    assert main(["keyword_volume", "--idea", "_fixture", "--dry-run", *argv]) == 2
    assert needle in capsys.readouterr().err


# --- ad_library --------------------------------------------------------------------------------


def ad_library(capsys, *argv):
    return run_json(capsys, ["ad_library", "--idea", "_fixture", "--dry-run", *argv])


def test_ad_library_meta(root, capsys):
    out = ad_library(capsys, "--engine", "meta", "--q", "ad account security")
    assert list(out) == ["engine", "query", "total_results", "items"]
    assert out["engine"] == "meta" and out["query"] == {
        "q": "ad account security",
        "country": "ALL",
    }
    assert out["total_results"] == 1460 and len(out["items"]) == 4
    assert out["items"][0] == {
        "advertiser": "Kestrelmark Security",
        "page_or_domain": "kestrelmark.example",
        "text": "Your ad account is a target. Turn on login alerts, audit every admin and get a "
        "free 10-point ad account security check in five minutes.",
        "format": "DCO",
        "first_seen": "2026-09-08T07:00:00Z",
        "last_seen": "2026-10-20T07:00:00Z",
        "active": True,
        "link": "https://kestrelmark.example/ad-account-security"
        "?utm_source=facebook&utm_medium=paid",
    }
    assert [item["active"] for item in out["items"]] == [True, True, False, True]
    assert out["items"][2]["format"] == "CAROUSEL"


def test_ad_library_tiktok(root, capsys):
    out = ad_library(capsys, "--engine", "tiktok", "--q", "ad account hacked", "--country", "FR")
    assert out["query"] == {"q": "ad account hacked", "country": "FR"}
    assert out["total_results"] == 11 and len(out["items"]) == 5
    assert out["items"][0] == {
        "advertiser": "Kestrelmark Security",
        "page_or_domain": None,
        "text": "Ad account hacked? Do these 3 things in the first hour",
        "format": "video",
        "first_seen": "2026-09-12T00:00:00Z",
        "last_seen": "2026-10-18T00:00:00Z",
        "active": None,
        "link": "https://cdn.example/tiktok/video/1900000000000001.mp4",
    }
    # an image ad links its first image
    assert out["items"][2]["link"] == "https://cdn.example/tiktok/image/1900000000000003-1.jpeg"


def test_ad_library_linkedin(root, capsys):
    out = ad_library(capsys, "--engine", "linkedin", "--q", "ad account security")
    assert out["total_results"] == 57 and len(out["items"]) == 4
    assert out["items"][0] == {
        "advertiser": "Kestrelmark Security",
        "page_or_domain": None,
        "text": "One leaked password can drain a quarter's ad budget. See how security teams "
        "watch ad account permissions.",
        "format": "image",
        "first_seen": None,
        "last_seen": None,
        "active": None,
        "link": "https://www.linkedin.com/ad-library/detail/900000101"
        "?trk=ad_library_ad_preview_content_image",
    }


def test_ad_library_google_transparency(root, capsys):
    out = ad_library(capsys, "--engine", "google_transparency", "--domain", "hootsuite.com")
    assert out["query"] == {"domain": "hootsuite.com", "region": "US", "num": 20}
    assert out["total_results"] == 200 and len(out["items"]) == 5
    assert out["items"][0] == {
        "advertiser": "Quarrytown Media LLC",
        "page_or_domain": "hootsuite.com",
        "text": None,
        "format": "text",
        "first_seen": "2026-08-11T14:02:51Z",
        "last_seen": "2026-10-19T22:47:03Z",
        "active": None,
        "link": "https://adstransparency.google.com/advertiser/AR09000000000000000001/creative/"
        "CR09000000000000000101?region=US",
    }


def test_ad_library_keeps_the_first_num_items(root, capsys):
    out = ad_library(capsys, "--engine", "meta", "--q", "x", "--num", "2")
    assert len(out["items"]) == 2 and out["total_results"] == 1460


@pytest.mark.parametrize(
    ("argv", "params"),
    [
        (
            ["--engine", "meta", "--q", "ad  account"],
            {"engine": "meta_ad_library", "q": "ad account"},
        ),
        (
            ["--engine", "meta", "--q", "ad account", "--country", "FR"],
            {"engine": "meta_ad_library", "q": "ad account", "country": "FR"},
        ),
        (
            ["--engine", "tiktok", "--q", "ad account", "--country", "all"],
            {"engine": "tiktok_ads_library", "q": "ad account"},
        ),
        (
            ["--engine", "linkedin", "--q", "ad account", "--country", "US"],
            {"engine": "linkedin_ad_library", "q": "ad account", "country": "US"},
        ),
        (
            ["--engine", "google_transparency", "--domain", "https://www.Hootsuite.com/"],
            {
                "engine": "google_ads_transparency_center",
                "domain": "hootsuite.com",
                "region": "US",
                "num": "20",
            },
        ),
        (
            ["--engine", "google_transparency", "--domain", "x.example", "--region", "anywhere"]
            + ["--num", "100"],
            {
                "engine": "google_ads_transparency_center",
                "domain": "x.example",
                "region": "anywhere",
                "num": "100",
            },
        ),
    ],
)
def test_ad_library_asks_each_library_its_own_way(root, capsys, monkeypatch, argv, params):
    seen = []
    wire(monkeypatch, searchapi, answer({}), seen)
    out = run_json(capsys, ["ad_library", "--idea", "_fixture", *argv])
    assert [dict(r.url.params) for r in seen] == [params]
    assert (out["total_results"], out["items"]) == (0, [])


@pytest.mark.parametrize("engine", ["meta", "tiktok", "linkedin", "google_transparency"])
def test_ad_library_reads_a_sparse_answer_without_failing(root, capsys, monkeypatch, engine):
    sparse = {
        "search_information": {"total_results": "1,234"},
        "ads": [{}, "junk", {"snapshot": None, "advertiser": None, "content": None}],
        "ad_creatives": [{}, "junk", {"advertiser": None}],
    }
    wire(monkeypatch, searchapi, answer(sparse))
    query = ["--domain", "x.example"] if engine == "google_transparency" else ["--q", "x"]
    out = run_json(capsys, ["ad_library", "--idea", "_fixture", "--engine", engine, *query])
    assert out["total_results"] == 1234
    assert out["items"] == [dict.fromkeys(ITEM_KEYS)] * 2


@pytest.mark.parametrize(
    ("engine", "ad", "field", "value"),
    [
        ("meta", {"snapshot": {"body": "plain text body"}}, "text", "plain text body"),
        (
            "meta",
            {"snapshot": {"body": {"text": ""}, "cards": [{"body": "card text"}]}},
            "text",
            "card text",
        ),
        ("meta", {"snapshot": {"title": "only a title"}}, "text", "only a title"),
        (
            "meta",
            {"snapshot": {"caption": "Shop.Example", "page_profile_uri": "https://fb.example/p"}},
            "page_or_domain",
            "shop.example",
        ),
        (
            "meta",
            {"snapshot": {"page_profile_uri": "https://www.facebook.com/900/"}},
            "page_or_domain",
            "https://www.facebook.com/900/",
        ),
        ("meta", {"page_name": "Top-level page"}, "advertiser", "Top-level page"),
        ("tiktok", {"advertiser": {"name": "As an object"}}, "advertiser", "As an object"),
        ("linkedin", {"content": {"title": "A document ad"}}, "text", "A document ad"),
        ("linkedin", {"headline": "An event ad"}, "text", "An event ad"),
        (
            "google_transparency",
            {"target_domain": "www.Shop.example"},
            "page_or_domain",
            "shop.example",
        ),
    ],
)
def test_ad_library_reads_each_field_where_the_ad_keeps_it(
    root, capsys, monkeypatch, engine, ad, field, value
):
    key = "ad_creatives" if engine == "google_transparency" else "ads"
    wire(monkeypatch, searchapi, answer({key: [ad]}))
    query = ["--domain", "x.example"] if engine == "google_transparency" else ["--q", "x"]
    out = run_json(capsys, ["ad_library", "--idea", "_fixture", "--engine", engine, *query])
    assert out["items"][0][field] == value


def test_ad_library_keeps_active_to_true_false_or_null(root, capsys, monkeypatch):
    ads = [{"page_name": "P", "is_active": "yes"}, {"page_name": "Q", "is_active": False}]
    wire(monkeypatch, searchapi, answer({"ads": ads}))
    out = run_json(capsys, ["ad_library", "--idea", "_fixture", "--engine", "meta", "--q", "x"])
    assert [item["active"] for item in out["items"]] == [None, False]
    assert main(["ad_library", "--idea", "_fixture", "--engine", "meta", "--q", "x"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[3].split() == ["P"] and lines[4].split() == ["Q", "no"]


def test_ad_library_summary(root, capsys):
    argv = [
        "ad_library",
        "--idea",
        "_fixture",
        "--dry-run",
        "--engine",
        "meta",
        "--q",
        "ad account",
    ]
    assert main(argv) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == 'meta: 1460 ads for "ad account" in ALL; the first 4:'
    assert lines[1].split() == [
        "advertiser",
        "page_or_domain",
        "format",
        "first_seen",
        "last_seen",
        "active",
        "text",
    ]
    assert lines[3].startswith("Kestrelmark Security") and "2026-09-08  2026-10-20  yes" in lines[3]
    assert lines[5].split()[0:5] == [
        "Pellucid",
        "Account",
        "Care",
        "pellucidcare.example",
        "CAROUSEL",
    ]
    assert "  no  " in lines[5] and len(lines) == 7


@pytest.mark.parametrize(
    ("argv", "needle"),
    [
        (["--q", "x"], "--engine is required"),
        (["--engine", "meta"], "meta needs --q"),
        (["--engine", "meta", "--domain", "x.com"], "--domain works with google_transparency only"),
        (["--engine", "linkedin", "--q", "x", "--region", "US"], "linkedin takes --country"),
        (["--engine", "google_transparency", "--q", "x"], "has no keyword search"),
        (["--engine", "google_transparency"], "google_transparency needs --domain"),
        (
            ["--engine", "google_transparency", "--domain", "x.com", "--country", "FR"],
            "takes --region",
        ),
        (["--engine", "google_transparency", "--domain", "x.com", "--num", "101"], "at most 100"),
    ],
)
def test_ad_library_refuses_a_query_its_library_cannot_run(root, capsys, argv, needle):
    assert main(["ad_library", "--idea", "_fixture", "--dry-run", *argv]) == 2
    err = capsys.readouterr().err
    assert needle in err and err.count("\n") == 1


@pytest.mark.parametrize(
    ("argv", "needle"),
    [
        (["--engine", "bing", "--q", "x"], "invalid choice: 'bing'"),
        (["--engine", "meta", "--q", "x", "--num", "0"], "'0' is not 1 or more"),
    ],
)
def test_ad_library_flags_are_checked_by_the_parser(root, capsys, argv, needle):
    assert main(["ad_library", "--idea", "_fixture", "--dry-run", *argv]) == 2
    assert needle in capsys.readouterr().err


def test_ad_library_logs_one_search(root, monkeypatch):
    wire(monkeypatch, searchapi, answer(fixture("searchapi/linkedin_ad_library")))
    before = costs.total("_fixture", kind="api")
    assert main(["ad_library", "--idea", "_fixture", "--engine", "linkedin", "--q", "x"]) == 0
    assert costs.total("_fixture", kind="api") == round(before + 0.01, 4)
    [path] = research(root, "ad_library")
    assert costs.read_lines("_fixture")[-1]["ref"] == path.name
