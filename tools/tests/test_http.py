import json
import time

import httpx
import pytest

from factory import http, secrets
from factory.http import Client, ProviderError
from factory.providers import searchapi

# --- the brief's tests -------------------------------------------------------------------------


def test_retry_then_ok(monkeypatch):
    seen = []

    def handler(req):
        seen.append(req.url.path)
        if len(seen) == 1:
            return httpx.Response(429, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"ok": 1})

    monkeypatch.setattr(time, "sleep", lambda s: None)
    c = Client("t", "https://x.test", transport=httpx.MockTransport(handler))
    assert c.get_json("/a") == {"ok": 1} and len(seen) == 2


def test_retry_then_error_redacts_key(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    c = Client(
        "t",
        "https://x.test",
        retries=2,
        transport=httpx.MockTransport(
            lambda r: httpx.Response(500, text="boom api_key=SECRETVALUE123")
        ),
    )
    with pytest.raises(ProviderError) as e:
        c.get_json("/a", params={"api_key": "SECRETVALUE123"})
    assert "SECRETVALUE123" not in str(e.value) and e.value.status == 500


def test_dry_run_reads_fixture():
    c = Client("searchapi", "https://x.test", dry_run=True)
    assert "organic_results" in c.get_json("/search", fixture="searchapi/google")


def test_pacing_sleeps(monkeypatch):
    slept = []
    monkeypatch.setattr(time, "sleep", slept.append)
    c = Client(
        "t",
        "https://x.test",
        pace_s=2.5,
        transport=httpx.MockTransport(lambda r: httpx.Response(200, json={})),
    )
    c.get_json("/a")
    c.get_json("/b")
    assert 2.5 in slept


# --- retries ---------------------------------------------------------------------------------


def replay(*responses):
    """A transport answering each request with the next of `responses` (an exception is raised)."""
    queue = list(responses)

    def handler(req):
        reply = queue.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply

    return httpx.MockTransport(handler)


def test_backoff_is_two_seconds_per_attempt_or_the_hint_capped(monkeypatch):
    slept = []
    monkeypatch.setattr(time, "sleep", slept.append)
    c = Client(
        "t",
        "https://x.test",
        retries=4,
        transport=replay(
            httpx.Response(503),
            httpx.Response(429, headers={"Retry-After": "30"}),
            httpx.Response(429, headers={"Retry-After": "9999"}),
            httpx.Response(200, json=[]),
        ),
    )
    assert c.get_json("/a") == []
    assert slept == [4, 30, 300]  # before attempts 2, 3, 4


def test_rate_limit_reset_is_seconds_or_a_unix_time(monkeypatch):
    slept = []
    monkeypatch.setattr(time, "sleep", slept.append)
    monkeypatch.setattr(time, "time", lambda: 1_800_000_000.0)
    c = Client(
        "t",
        "https://x.test",
        transport=replay(
            httpx.Response(429, headers={"X-RateLimit-Reset": "7"}),
            httpx.Response(429, headers={"X-RateLimit-Reset": "1800000050"}),
            httpx.Response(200, json={}),
        ),
    )
    assert c.get_json("/a") == {}
    assert slept == [7, 50]


def test_network_errors_count_as_failed_attempts(monkeypatch):
    slept = []
    monkeypatch.setattr(time, "sleep", slept.append)
    c = Client(
        "t",
        "https://x.test",
        transport=replay(httpx.ConnectError("refused"), httpx.Response(200, json={"ok": 1})),
    )
    assert c.get_json("/a") == {"ok": 1} and slept == [4]

    c = Client("t", "https://x.test", retries=2, transport=replay(*[httpx.ReadTimeout("slow")] * 2))
    with pytest.raises(ProviderError) as e:
        c.get("/a")
    assert e.value.status is None
    assert str(e.value) == "t: network error: GET /a: ReadTimeout: slow"


def test_get_returns_any_final_status_without_retrying_4xx(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(404, text="not\nfound")

    c = Client("rdap", "https://x.test", transport=httpx.MockTransport(handler))
    assert c.get("/domain/x.com").status_code == 404 and len(seen) == 1
    with pytest.raises(ProviderError) as e:
        c.get_json("/domain/x.com")
    assert str(e.value) == "rdap: HTTP 404: GET /domain/x.com: not found" and len(seen) == 2

    c = Client("t", "https://x.test", retries=2, transport=replay(*[httpx.Response(502)] * 2))
    assert c.get("/a").status_code == 502  # retried out: returned, not raised


def test_retry_on_extends_the_retry_predicate(monkeypatch):
    slept = []
    monkeypatch.setattr(time, "sleep", slept.append)
    c = Client(
        "arcticshift",
        "https://x.test",
        retry_on=lambda r: r.status_code == 422 and "slow down" in r.text,
        transport=replay(
            httpx.Response(422, text="slow down", headers={"X-RateLimit-Reset": "12"}),
            httpx.Response(200, json={"data": [1]}),
        ),
    )
    assert c.get_json("/api/posts/search") == {"data": [1]} and slept == [12]


def test_json_calls_accept_any_2xx_and_refuse_non_json():
    c = Client("t", "https://x.test", transport=replay(httpx.Response(201, json=[{"a": 1}])))
    assert c.post_json("/rows/", json={"keywords": ["a"]}) == [{"a": 1}]

    c = Client(
        "t", "https://x.test", transport=replay(httpx.Response(200, text="<html>down</html>"))
    )
    with pytest.raises(ProviderError, match=r"^t: HTTP 200: GET /a: not JSON: <html>down</html>$"):
        c.get_json("/a")


QUOTA_BODY = {
    "error": "You have used all of the searches for the month. Please upgrade your plan on SearchApi.io."
}


def test_quota_used_up_is_fatal_one_request_no_sleep(monkeypatch):
    slept = []
    monkeypatch.setattr(time, "sleep", slept.append)
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(429, json=QUOTA_BODY)

    c = Client(
        "searchapi",
        "https://x.test",
        pace_s=0.35,
        fatal=searchapi.quota_used_up,
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(ProviderError) as e:
        c.get("/search", params={"engine": "google", "api_key": "SECRETVALUE123"})
    assert len(seen) == 1 and slept == [] and e.value.status == 429
    assert str(e.value).startswith("searchapi: HTTP 429: GET /search?engine=google&api_key=***: ")
    assert "You have used all of the searches for the month" in str(e.value)
    assert "SECRETVALUE123" not in str(e.value)


def test_an_ordinary_429_still_retries_with_the_fatal_hook(monkeypatch):
    slept = []
    monkeypatch.setattr(time, "sleep", slept.append)
    c = Client(
        "searchapi",
        "https://x.test",
        fatal=searchapi.quota_used_up,
        transport=replay(
            httpx.Response(429, json={"error": "Too many requests, slow down."}),
            httpx.Response(200, json={"ok": 1}),
        ),
    )
    assert c.get_json("/search") == {"ok": 1} and slept == [4]


# --- pacing ----------------------------------------------------------------------------------


def test_pacing_counts_from_the_previous_request_start(monkeypatch):
    now = [1000.0]
    slept = []

    def sleep(seconds):
        slept.append(seconds)
        now[0] += seconds

    def handler(req):
        now[0] += {"/slow": 3.0, "/fast": 1.0}[req.url.path]  # how long the request takes
        return httpx.Response(200, json={})

    monkeypatch.setattr(time, "monotonic", lambda: now[0])
    monkeypatch.setattr(time, "sleep", sleep)
    c = Client("t", "https://x.test", pace_s=2.5, transport=httpx.MockTransport(handler))
    c.get_json("/slow")  # the first request never waits
    c.get_json("/fast")  # 3 s since the previous start: no wait
    c.get_json("/fast")  # 1 s since the previous start: wait the remaining 1.5 s
    assert slept == [1.5]


# --- requests, dry runs ------------------------------------------------------------------------


def test_client_params_and_headers_ride_on_every_request():
    seen = []

    def handler(req):
        seen.append(req)
        return httpx.Response(200, json={})

    c = Client(
        "t",
        "https://x.test/api/v1",
        headers={"Authorization": "Token abc"},
        params={"api_key": "k"},
        transport=httpx.MockTransport(handler),
    )
    c.get_json("/search", params={"q": "a b", "unset": None})
    c.post_json("/rows/", json={"x": 1})
    assert [r.url.path for r in seen] == ["/api/v1/search", "/api/v1/rows/"]
    assert dict(seen[0].url.params) == {"api_key": "k", "q": "a b"}
    assert all(r.headers["Authorization"] == "Token abc" for r in seen)
    assert c.calls == 2


def test_dry_run_makes_no_request_counts_calls_and_names_a_missing_fixture():
    c = Client("searchapi", "https://x.test", dry_run=True)
    response = c.get("/search", params={"q": "x"}, fixture="searchapi/google")
    assert response.status_code == 200 and "organic_results" in response.json()
    assert c.post_json("/research/us/analyze-keywords/", fixture="seranking/analyze_keywords")
    assert c.calls == 2
    with pytest.raises(FileNotFoundError, match=r"fixtures/searchapi/nope\.json"):
        c.get_json("/search", fixture="searchapi/nope")


def fixture_dir(monkeypatch, tmp_path, files: dict):
    """Point the dry-run fixtures at tmp_path, holding `files` ({"provider/name": data})."""
    for name, data in files.items():
        path = tmp_path / f"{name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(http, "FIXTURES", tmp_path)


def test_dry_run_answers_with_the_fixture_status_and_the_rest_as_the_body(monkeypatch, tmp_path):
    fixture_dir(
        monkeypatch,
        tmp_path,
        {"t/missing": {"_status": 404}, "t/made": {"_status": 201, "id": 7}, "t/plain": {"a": 1}},
    )
    c = Client("t", "https://x.test", dry_run=True)
    missing = c.get("/domain/x.io", fixture="t/missing")
    assert missing.status_code == 404 and missing.json() == {}
    assert c.post_json("/rows/", json={"x": 1}, fixture="t/made") == {"id": 7}
    plain = c.get("/a", fixture="t/plain")
    assert plain.status_code == 200 and plain.json() == {"a": 1}
    assert c.calls == 3


def test_dry_run_json_calls_refuse_a_non_2xx_fixture_status_like_a_real_answer(
    monkeypatch, tmp_path
):
    fixture_dir(monkeypatch, tmp_path, {"t/missing": {"_status": 404}})
    c = Client("t", "https://x.test", dry_run=True)
    with pytest.raises(ProviderError) as e:
        c.get_json("/domain/x.io", fixture="t/missing")
    assert e.value.status == 404 and str(e.value) == "t: HTTP 404: GET /domain/x.io: {}"
    with pytest.raises(ProviderError) as e:
        c.post_json("/domain/x.io", fixture="t/missing")
    assert e.value.status == 404


def test_the_rdap_fixtures_answer_404_and_200():
    c = Client("rdap", "https://rdap.org", dry_run=True)
    assert c.get("/domain/x.io", fixture="rdap/available").status_code == 404
    taken = c.get("/domain/example.com", fixture="rdap/taken")
    assert taken.status_code == 200 and "_status" not in taken.json()


# --- ProviderError -----------------------------------------------------------------------------


def test_ok_calls_counts_only_the_calls_answered_with_a_2xx(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda s: None)
    c = Client(
        "searchapi",
        "https://x.test",
        retries=2,
        fatal=searchapi.quota_used_up,
        transport=replay(
            httpx.Response(200, json={}),  # /a: answered
            httpx.Response(500),  # /b: answered on its retry
            httpx.Response(201, json={}),
            httpx.Response(500),  # /c: failed after its retries
            httpx.Response(503),
            httpx.Response(404),  # /d: an answer, not a 2xx
            httpx.ConnectError("refused"),  # /e: never answered
            httpx.ConnectError("refused"),
            httpx.Response(429, json=QUOTA_BODY),  # /f: the used-up quota, fatal at once
        ),
    )
    assert c.get_json("/a") == {} and c.post_json("/b") == {}
    with pytest.raises(ProviderError):
        c.get_json("/c")
    assert c.get("/d").status_code == 404
    for path in ("/e", "/f"):
        with pytest.raises(ProviderError):
            c.get(path)
    assert (c.calls, c.ok_calls) == (6, 2)


def test_a_dry_run_counts_its_2xx_answers_as_ok_calls(monkeypatch, tmp_path):
    fixture_dir(monkeypatch, tmp_path, {"t/missing": {"_status": 404}, "t/plain": {"a": 1}})
    c = Client("t", "https://x.test", dry_run=True)
    c.get("/a", fixture="t/plain")
    c.get("/b", fixture="t/missing")
    assert (c.calls, c.ok_calls) == (2, 1)


def test_provider_error_redacts_known_secrets_and_credential_params(monkeypatch):
    monkeypatch.setattr(
        secrets, "load", lambda *a, **k: {"providers": {"x": {"t": "tok-abcdef-123"}}}
    )
    e = ProviderError("seranking", 401, "Token tok-abcdef-123 refused\n(try ?token=zzz&key=yy)")
    assert str(e) == "seranking: HTTP 401: Token *** refused (try ?token=***&key=***)"
    assert ProviderError("t", 500, "x" * 400).detail == "x" * 300
