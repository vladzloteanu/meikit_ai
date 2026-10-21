import functools
import importlib.util
import json
import time
from pathlib import Path

import httpx
import pytest

from factory import secrets
from factory.http import Client
from factory.providers import searchapi, seranking

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "capture-fixtures.py"
KEY = "sapi-test-key-123456"
TOKEN = "ser-test-token-123456"
QUOTA_BODY = {"error": "You have used all of the searches for the month. Please upgrade your plan."}


@pytest.fixture
def script(monkeypatch, tmp_path):
    """scripts/capture-fixtures.py as a module that writes into tmp_path, with fake secrets."""
    spec = importlib.util.spec_from_file_location("capture_fixtures", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    config = {"providers": {"searchapi": {"api_key": KEY}, "seranking": {"api_token": TOKEN}}}
    monkeypatch.setattr(secrets, "load", lambda *a, **k: config)
    monkeypatch.setattr(time, "sleep", lambda s: None)
    monkeypatch.setattr(module, "FIXTURES", tmp_path)
    return module


def serve(monkeypatch, handler):
    """Every provider client talks to `handler` instead of the network; returns the requests."""
    seen = []

    def recording(req):
        seen.append(req)
        return handler(req)

    for module in (searchapi, seranking):
        transport = httpx.MockTransport(recording)
        monkeypatch.setattr(module, "Client", functools.partial(Client, transport=transport))
    return seen


def searchapi_answer(req):
    """A SearchAPI-like answer that echoes the key the way the real one does, with 12 items."""
    items = [{"position": n, "link": str(req.url)} for n in range(1, 13)]
    return httpx.Response(
        200,
        json={
            "search_metadata": {"request_url": str(req.url)},
            "search_parameters": dict(req.url.params),
            "search_information": {"total_results": 12},
            "ads": items,
            "organic_results": items,
            "ad_creatives": items,
            "pagination": {"next_page_token": "abc"},
        },
    )


def test_capture_trims_strips_and_redacts(script, tmp_path, monkeypatch, capsys):
    serve(monkeypatch, searchapi_answer)
    assert script.main(["--only", "searchapi"]) == 0
    files = sorted(tmp_path.glob("searchapi/*.json"))
    assert [f.stem for f in files] == sorted(script.SEARCHAPI_CALLS)
    for file in files:
        text = file.read_text()
        data = json.loads(text)
        assert set(data) == {
            "search_parameters",
            "search_information",
            "ads",
            "organic_results",
            "ad_creatives",
        }
        assert "api_key" not in data["search_parameters"] and len(data["ads"]) == 10
        assert KEY not in text and "api_key=***" in text
    out = capsys.readouterr()
    assert KEY not in out.out + out.err and "secret check: OK" in out.out


def test_a_quota_429_touches_no_file(script, tmp_path, monkeypatch, capsys):
    seen = serve(monkeypatch, lambda req: httpx.Response(429, json=QUOTA_BODY))
    assert script.main([]) == 1
    assert len(seen) == 1 and list(tmp_path.iterdir()) == []
    err = capsys.readouterr().err
    assert "used all of the searches" in err and KEY not in err


def test_a_written_file_holding_a_secret_is_deleted(script, tmp_path, monkeypatch, capsys):
    serve(monkeypatch, lambda req: httpx.Response(200, json=[{"keyword": TOKEN}]))
    monkeypatch.setattr(secrets, "redact", lambda text, **k: text)  # a broken redact
    assert script.main(["--only", "seranking"]) == 1
    assert list(tmp_path.glob("seranking/*.json")) == []
    out = capsys.readouterr()
    assert "secret check: FAILED" in out.out and TOKEN not in out.out + out.err
