import functools
import json
import re
import time

import httpx
import pytest

from factory import secrets
from factory.http import FIXTURES, Client
from factory.providers import searchapi, seranking

# --- the brief's tests -------------------------------------------------------------------------


def test_analyze_keywords_posts_json_batches():
    bodies = []

    def handler(req):
        bodies.append(json.loads(req.content))
        rows = [
            {"keyword": k, "volume": 10, "cpc": 0, "is_data_found": True}
            for k in bodies[-1]["keywords"]
        ]
        return httpx.Response(201, json=rows)

    c = Client("seranking", "https://x.test", transport=httpx.MockTransport(handler))
    rows = seranking.analyze_keywords(c, "us", [f"kw{i}" for i in range(25)])
    assert len(rows) == 25 and len(bodies) == 2 and bodies[0]["keywords"][0] == "kw0"


def test_cc_mapping():
    assert seranking.cc("GB") == "uk" and seranking.cc("FR") == "fr"


# --- the real clients, against a mock transport ------------------------------------------------


def wire(monkeypatch, module, keys: dict, reply):
    """Make `module.client()` read `keys` as its secrets and talk to a transport answering `reply`."""
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(200, json=reply)

    monkeypatch.setattr(secrets, "get", lambda dotpath, *a, **k: keys[dotpath])
    monkeypatch.setattr(time, "sleep", lambda s: None)  # SE Ranking's 2.5 s pacing
    monkeypatch.setattr(
        module, "Client", functools.partial(Client, transport=httpx.MockTransport(handler))
    )
    return seen


def test_searchapi_sends_the_engine_the_params_and_the_key(monkeypatch):
    seen = wire(
        monkeypatch, searchapi, {"providers.searchapi.api_key": "sapi-test-key"}, {"ads": []}
    )
    c = searchapi.client()
    assert searchapi.search(c, "google", q="ad account hacked", gl="us") == {"ads": []}
    url = seen[0].url
    assert (url.host, url.path) == ("www.searchapi.io", "/api/v1/search")
    assert dict(url.params) == {
        "api_key": "sapi-test-key",
        "engine": "google",
        "q": "ad account hacked",
        "gl": "us",
    }
    assert c.pace_s == 0.35 and c.fatal is searchapi.quota_used_up


def test_seranking_sends_the_token_and_the_domain_queries(monkeypatch):
    seen = wire(monkeypatch, seranking, {"providers.seranking.api_token": "ser-test-token"}, [])
    c = seranking.client()
    seranking.domain_keywords(c, "GB", "hootsuite.com")
    seranking.domain_advertising(c, "us", "hootsuite.com")
    seranking.domain_overview(c, "us", "hootsuite.com")
    assert [(r.method, r.url.path, dict(r.url.params)) for r in seen] == [
        ("GET", "/research/uk/keywords/", {"domain": "hootsuite.com", "limit": "60"}),
        ("GET", "/research/us/advertising/", {"domain": "hootsuite.com"}),
        ("GET", "/research/us/overview/", {"domain": "hootsuite.com"}),
    ]
    assert {r.url.host for r in seen} == {"api4.seranking.com"}
    assert all(r.headers["Authorization"] == "Token ser-test-token" for r in seen)
    assert c.pace_s == 2.5


# --- dry runs and the captured fixtures --------------------------------------------------------


@pytest.fixture
def no_secrets(monkeypatch):
    """Any read of a secret fails the test: a dry run must not need one."""
    monkeypatch.setattr(secrets, "get", lambda *a, **k: pytest.fail("a dry run read a secret"))


@pytest.mark.parametrize(
    ("engine", "items"),
    [
        ("google", "organic_results"),
        ("meta_ad_library", "ads"),
        ("tiktok_ads_library", "ads"),
        ("google_ads_transparency_center", "ad_creatives"),
        ("linkedin_ad_library", "ads"),
    ],
)
def test_searchapi_dry_run_serves_each_engine_fixture(no_secrets, engine, items):
    data = searchapi.search(searchapi.client(dry_run=True), engine, q="anything")
    assert data["search_parameters"]["engine"] == engine
    assert 0 < len(data[items]) <= 10 and "search_metadata" not in data


def test_seranking_dry_run_serves_the_fixtures(no_secrets):
    c = seranking.client(dry_run=True)
    rows = seranking.analyze_keywords(
        c, "us", ["facebook ad account hacked", "business manager hacked"]
    )
    assert [r["keyword"] for r in rows] == ["facebook ad account hacked", "business manager hacked"]
    for row in rows:  # SE Ranking's US base has neither keyword: a row then holds only these two
        assert {"keyword", "is_data_found"} <= set(row)
        if row["is_data_found"]:
            assert {
                "volume",
                "cpc",
                "difficulty",
                "competition",
                "intents",
                "history_trend",
            } <= set(row)
    assert 0 < len(seranking.domain_keywords(c, "us", "hootsuite.com")) <= 10
    assert 0 < len(seranking.domain_advertising(c, "us", "hootsuite.com")) <= 10
    assert isinstance(seranking.domain_overview(c, "us", "hootsuite.com"), dict)
    assert c.calls == 4


def test_fixtures_carry_no_request_metadata_or_key_param():
    files = sorted(FIXTURES.glob("*/*.json"))
    assert len(files) == 9
    for file in files:
        text = file.read_text(encoding="utf-8")
        assert "search_metadata" not in text, file.name
        assert not re.search(r"(?i)\bapi_key=(?!\*\*\*)", text), file.name  # SearchAPI's key
