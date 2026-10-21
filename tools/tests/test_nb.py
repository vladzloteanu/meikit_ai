import copy
import functools
import json

import httpx
import pytest

from factory import costs, secrets
from factory.cli import main
from factory.http import FIXTURES, Client, ProviderError
from factory.providers import neuralbox
from factory.tools import nb

KEY = "KEY12345678"
EMAIL = "factory@example.test"
WHITELIST = [
    "mcp__tools__LookupAdsInsights",
    "mcp__tools__ListCategories",
    "mcp__tools__QueryAdsInsights",
]
STRUCTURED = {
    "category_resolved": "Home Security",
    "countries": ["FR", "US"],
    "networks": [
        {
            "network": "facebook",
            "total_reach": 24500000,
            "advertisers_count": 312,
            "top_companies": [
                {"name": "Alarmo Example", "share_pct": 12.7},
                {"name": "Securis Example", "share_pct": 8.1},
            ],
            "caveats": ["reach is per network"],
        },
        {
            "network": "search",
            "total_reach": None,
            "advertisers_count": None,
            "top_companies": [],
            "caveats": ["QueryAdsInsights failed: timeout"],
        },
    ],
    "typical_hooks": ["free installation", "24/7 monitoring"],
    "not_found": False,
}
ASK = ["nb", "ask", "--idea", "_fixture", "--prompt", "hi"]
ADSINSIGHTS = [
    "nb",
    "adsinsights",
    "--idea",
    "_fixture",
    "--category",
    "home security",
    "--countries",
    "FR,US",
]


def research(root, tool):
    return sorted((root / "ideas/_fixture/research").glob(f"{tool}_*"))


def fixture(name):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def reply(**fields):
    """A /respond answer as NeuralBox shapes it (ChatResponse), `fields` over a plain one."""
    body = {
        "request_id": "req-1",
        "answer": "ok",
        "explanation": None,
        "structured_output": None,
        "session_id": "sess-1",
        "tools_called": [],
        "cost_usd": 0.25,
        "errors": [],
    }
    return {**body, **fields}


def heartbeat(*tools):
    return {"status": "ok", "server_version": "0.1.0", "available_tools": list(tools)}


def wire(monkeypatch, *answers):
    """Make `neuralbox.client()` a mock client answering each request with the next of `answers`
    (a JSON body answered 200, or an httpx.Response). Returns the requests sent."""
    seen = []
    queue = list(answers)

    def handler(request):
        seen.append(request)
        answer = queue.pop(0)
        return answer if isinstance(answer, httpx.Response) else httpx.Response(200, json=answer)

    monkeypatch.setattr(
        neuralbox,
        "client",
        lambda dry_run=False: neuralbox.NeuralBoxClient(
            "neuralbox",
            "https://nb.test",
            headers={"X-API-Key": KEY},
            retries=1,
            transport=httpx.MockTransport(handler),
            user_email=EMAIL,
        ),
    )
    return seen


def body_of(request):
    return json.loads(request.content)


@pytest.fixture
def no_secrets(monkeypatch):
    """Any read of a secret fails the test: a dry run must not need one."""
    monkeypatch.setattr(secrets, "get", lambda *a, **k: pytest.fail("a dry run read a secret"))


# --- the brief's tests -------------------------------------------------------------------------


def test_respond_body_and_headers(root):
    seen = {}

    def handler(req):
        seen["headers"] = dict(req.headers)
        seen["body"] = json.loads(req.content)
        return httpx.Response(
            200,
            json={
                "request_id": "r1",
                "answer": "pong",
                "structured_output": {"a": 1},
                "cost_usd": 0.01,
                "tools_called": [{"name": "X", "input": {"k": "v"}}],
                "session_id": "s1",
            },
        )

    c = Client(
        "neuralbox",
        "https://nb.test",
        headers={"X-API-Key": "KEY12345678"},
        transport=httpx.MockTransport(handler),
    )
    r = neuralbox.respond(c, "ping", allowed_tools=["X"], schema={"type": "object"}, max_turns=2)
    assert seen["headers"]["x-api-key"] == "KEY12345678"
    b = seen["body"]
    assert (
        b["permission_mode"] == "bypassPermissions"
        and b["allowed_tools"] == ["X"]
        and b["output_format"]["type"] == "json_schema"
        and b["prompt"].endswith("Never print secret values.")
    )
    assert r.structured == {"a": 1} and r.tools_called == ["X"] and r.cost_usd == 0.01


def test_nb_ask_logs_cost_and_hides_key(root, monkeypatch, capsys):
    monkeypatch.setattr(
        neuralbox,
        "client",
        lambda dry_run=False: Client(
            "neuralbox",
            "https://nb.test",
            headers={"X-API-Key": "KEY12345678"},
            transport=httpx.MockTransport(
                lambda r: httpx.Response(
                    200,
                    json={"request_id": "r1", "answer": "ok", "cost_usd": 1.0, "tools_called": []},
                )
            ),
        ),
    )
    assert main(["nb", "ask", "--idea", "_fixture", "--prompt", "hi"]) == 0
    f = next((root / "ideas/_fixture/research").glob("nb_*.json"))
    assert "KEY12345678" not in f.read_text()
    assert (
        abs(costs.total("_fixture", kind="llm") - 0.92) < 1e-6
        or costs.total("_fixture", kind="llm") >= 0.92
    )


def test_nb_refuses_over_cap(root, capsys):
    costs.append("_fixture", "ads", "meta", 300.0)
    assert main(["nb", "ask", "--idea", "_fixture", "--prompt", "hi", "--dry-run"]) == 1
    assert "cap" in capsys.readouterr().err


def test_adsinsights_persists_structured_only(root, monkeypatch):
    monkeypatch.setattr(
        neuralbox,
        "client",
        lambda dry_run=False: Client(
            "neuralbox",
            "https://nb.test",
            transport=httpx.MockTransport(
                lambda r: httpx.Response(
                    200,
                    json={
                        "request_id": "r",
                        "answer": "RAW ROWS HERE",
                        "structured_output": {
                            "category_resolved": "Home Security",
                            "countries": ["FR"],
                            "networks": [],
                            "typical_hooks": [],
                            "not_found": False,
                        },
                        "cost_usd": 0.3,
                        "tools_called": [],
                    },
                )
            ),
        ),
    )
    main(
        [
            "nb",
            "adsinsights",
            "--idea",
            "_fixture",
            "--category",
            "home security",
            "--countries",
            "FR",
        ]
    )
    f = next((root / "ideas/_fixture/research").glob("nb_adsinsights_*.json"))
    assert "RAW ROWS HERE" not in f.read_text()


# --- the provider ------------------------------------------------------------------------------


def test_respond_names_the_factory_and_leaves_out_what_is_not_given(monkeypatch):
    seen = wire(monkeypatch, reply())
    neuralbox.respond(neuralbox.client(), "ping")
    [request] = seen
    assert (request.method, request.url.path) == ("POST", "/respond")
    body = body_of(request)
    # NeuralBox refuses a call whose properties lack a project and a user name (422), or a user
    # email it knows (400/403); NeuralBox stops the run before the client gives up on it.
    assert body == {
        "prompt": "ping" + neuralbox.DISCIPLINE,
        "permission_mode": "bypassPermissions",
        "max_turns": 8,
        "timeout": neuralbox.RUN_TIMEOUT_S,
        "properties": {
            "project": "astrafable",
            "user_name": "astrafable-factory",
            "user_email": EMAIL,
        },
    }
    assert neuralbox.RUN_TIMEOUT_S < neuralbox.TIMEOUT_S


def test_respond_sends_the_whitelist_the_schema_and_the_session(monkeypatch):
    seen = wire(monkeypatch, reply())
    schema = {"type": "object", "properties": {"a": {"type": "integer"}}}
    neuralbox.respond(
        neuralbox.client(),
        "ping",
        allowed_tools=["mcp__tools__QueryAdsInsights"],
        schema=schema,
        max_turns=3,
        session_id="sess-0",
    )
    body = body_of(seen[0])
    assert body["allowed_tools"] == ["mcp__tools__QueryAdsInsights"]
    assert body["output_format"] == {"type": "json_schema", "schema": schema}
    assert (body["max_turns"], body["session_id"]) == (3, "sess-0")


def test_discipline_is_the_briefs():
    assert neuralbox.DISCIPLINE == (
        "\n\nIf a tool call fails or a key is missing, say exactly which tool failed. "
        "Never invent numbers. Never print secret values."
    )


def test_respond_keeps_the_tool_names_only(monkeypatch):
    calls = [
        {"name": "mcp__tools__LookupAdsInsights", "input": {"q": "x"}, "output": "RAW"},
        {"name": "mcp__tools__QueryAdsInsights", "input": {"section": "aggregations"}},
        {"input": {}},  # no name: not a tool call it can report
    ]
    wire(monkeypatch, reply(tools_called=calls, structured_output={"a": 1}))
    result = neuralbox.respond(neuralbox.client(), "ping")
    assert result == neuralbox.NBResult(
        answer="ok",
        structured={"a": 1},
        cost_usd=0.25,
        tools_called=["mcp__tools__LookupAdsInsights", "mcp__tools__QueryAdsInsights"],
        session_id="sess-1",
        request_id="req-1",
        errors=[],
    )


def test_respond_reads_a_missing_cost_as_none_and_keeps_the_errors(monkeypatch):
    wire(
        monkeypatch,
        reply(cost_usd=None, answer=None, errors=["Query timed out\n(timeout=540s)"], session_id=7),
    )
    result = neuralbox.respond(neuralbox.client(), "ping")
    assert result.cost_usd is None and result.answer == "" and result.session_id is None
    assert result.errors == ["Query timed out (timeout=540s)"]


@pytest.mark.parametrize(
    ("fields", "errors", "tools"),
    [
        ({"errors": "boom", "tools_called": "Read"}, [], []),  # not lists: nothing to read
        ({"errors": ["", "  ", None, "real\nerror"]}, ["real error"], []),  # blanks are no error
        ({"cost_usd": -1.0}, [], []),
        ({"cost_usd": True}, [], []),
    ],
)
def test_respond_reads_odd_answers_without_failing(monkeypatch, fields, errors, tools):
    wire(monkeypatch, reply(**fields))
    result = neuralbox.respond(neuralbox.client(), "ping")
    assert (result.errors, result.tools_called) == (errors, tools)
    if "cost_usd" in fields:
        assert result.cost_usd is None


@pytest.mark.parametrize("status", [403, 500])
def test_a_refused_call_is_one_line_and_never_retried(monkeypatch, status):
    body = {"error": "User not found: someone@example.test"}
    seen = wire(monkeypatch, httpx.Response(status, json=body))
    with pytest.raises(ProviderError) as caught:
        neuralbox.respond(neuralbox.client(), "ping")
    assert len(seen) == 1  # a second attempt would run, and bill, the agent again
    message = str(caught.value)
    assert message.startswith(f"neuralbox: HTTP {status}: POST /respond: ")
    assert "\n" not in message and KEY not in message


def test_an_answer_that_is_not_an_object_is_a_provider_error(monkeypatch):
    wire(monkeypatch, ["not", "an", "object"])
    with pytest.raises(
        ProviderError, match="neuralbox: HTTP 200: POST /respond: not a JSON object"
    ):
        neuralbox.respond(neuralbox.client(), "ping")


def test_the_client_reads_the_url_the_key_and_the_user(monkeypatch):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json=reply())

    config = {"nb.url": "http://127.0.0.1:3076", "nb.api_key": KEY, "nb.user_email": EMAIL}
    monkeypatch.setattr(secrets, "get", lambda dotpath, *a, **k: config[dotpath])
    monkeypatch.setattr(
        neuralbox,
        "NeuralBoxClient",
        functools.partial(neuralbox.NeuralBoxClient, transport=httpx.MockTransport(handler)),
    )
    c = neuralbox.client()
    neuralbox.respond(c, "ping")
    [request] = seen
    assert str(request.url) == "http://127.0.0.1:3076/respond"
    assert request.headers["X-API-Key"] == KEY
    assert body_of(request)["properties"]["user_email"] == EMAIL
    assert (c.retries, c.user_email) == (1, EMAIL)
    assert c._http.timeout == httpx.Timeout(600.0)


def test_heartbeat_gets_the_tool_list(monkeypatch):
    seen = wire(monkeypatch, heartbeat("Read", *WHITELIST))
    assert neuralbox.heartbeat(neuralbox.client())["available_tools"] == ["Read", *WHITELIST]
    assert (seen[0].method, seen[0].url.path) == ("GET", "/heartbeat")


def test_a_dry_run_client_reads_no_secret_and_answers_from_the_fixtures(no_secrets):
    c = neuralbox.client(dry_run=True)
    assert len(neuralbox.heartbeat(c)["available_tools"]) == 10
    result = neuralbox.respond(c, "anything")
    assert result.answer and result.request_id and result.cost_usd > 0
    ads = neuralbox.respond(c, "anything", fixture="neuralbox/adsinsights")
    assert ads.structured["category_resolved"] and ads.tools_called
    assert c.calls == 3


# --- the fixtures ------------------------------------------------------------------------------


def test_the_heartbeat_fixture_lists_the_whitelist():
    tools = fixture("neuralbox/heartbeat")["available_tools"]
    assert len(tools) == 10 and set(WHITELIST) <= set(tools)


def test_the_adsinsights_fixture_holds_invented_companies_within_the_schema():
    answer = fixture("neuralbox/adsinsights")
    structured = answer["structured_output"]
    assert nb.conclusions(nb.ADSINSIGHTS_SCHEMA, structured) == structured
    names = [c["name"] for n in structured["networks"] for c in n["top_companies"]]
    assert names and all(name.endswith(" Example") for name in names)
    assert {call["name"] for call in answer["tools_called"]} <= set(WHITELIST)


# --- nb ask ------------------------------------------------------------------------------------


def test_ask_writes_the_answer_and_logs_its_cost(root, tmp_path, capsys, monkeypatch):
    schema = {"type": "object", "properties": {"a": {"type": "integer"}}}
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps(schema), encoding="utf-8")
    calls = [{"name": "mcp__SearchAPI__GoogleSearch", "input": {"q": "x"}, "output": "RAW"}]
    seen = wire(monkeypatch, reply(structured_output={"a": 1}, tools_called=calls))
    argv = [*ASK, "--tools", "mcp__SearchAPI__GoogleSearch,WebSearch", "--schema", str(schema_file)]
    assert main([*argv, "--max-turns", "3", "--session", "sess-0"]) == 0
    body = body_of(seen[0])
    assert body["allowed_tools"] == ["mcp__SearchAPI__GoogleSearch", "WebSearch"]
    assert body["output_format"]["schema"] == schema
    assert (body["max_turns"], body["session_id"]) == (3, "sess-0")
    [path] = research(root, "nb_ask")
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "prompt": "hi",
        "answer": "ok",
        "structured": {"a": 1},
        "cost_usd": 0.25,
        "tools_called": ["mcp__SearchAPI__GoogleSearch"],
        "session_id": "sess-1",
        "request_id": "req-1",
    }
    line = costs.read_lines("_fixture")[-1]
    assert (line["kind"], line["provider"], line["ref"]) == ("llm", "neuralbox", "req-1")
    assert line["amount_eur"] == round(0.25 * costs.USD_EUR, 4) and line["phase"] == "triage"
    assert line["note"] == "nb ask, 0.25 USD"
    out, err = capsys.readouterr()
    assert out.startswith("ok\n") and '"a": 1' in out
    assert "tools called: mcp__SearchAPI__GoogleSearch" in out
    assert err.startswith("nb_ask: wrote ideas/_fixture/research/nb_ask_")
    assert err.rstrip().endswith("0.23 EUR (nb ask, 0.25 USD) logged")


def test_ask_reads_the_prompt_from_a_file_and_sends_it_with_the_discipline(
    root, tmp_path, monkeypatch
):
    prompt = tmp_path / "prompt.md"
    prompt.write_text("How many advertisers?\nOne line more.\n", encoding="utf-8")
    seen = wire(monkeypatch, reply())
    assert main(["nb", "ask", "--idea", "_fixture", "--prompt-file", str(prompt)]) == 0
    sent = body_of(seen[0])["prompt"]
    assert sent == "How many advertisers?\nOne line more.\n" + neuralbox.DISCIPLINE
    [path] = research(root, "nb_ask")
    assert json.loads(path.read_text())["prompt"] == "How many advertisers?\nOne line more.\n"


@pytest.mark.parametrize(
    ("extra", "needle"),
    [
        ([], "--prompt"),
        (["--prompt", "  "], "the prompt is empty"),
        (["--prompt-file", "/no/such/prompt.md"], "cannot read /no/such/prompt.md"),
        (["--prompt", "hi", "--schema", "/no/such/schema.json"], "cannot read"),
        (["--prompt", "hi", "--tools", " , "], "--tools"),
        (["--prompt", "hi", "--prompt-file", "f.md"], "not allowed with argument"),
        (["--prompt", "hi", "--max-turns", "0"], "is not 1 or more"),
    ],
)
def test_ask_refuses_a_command_line_it_cannot_run(root, capsys, monkeypatch, extra, needle):
    monkeypatch.setattr(neuralbox, "client", lambda dry_run=False: pytest.fail("client built"))
    assert main(["nb", "ask", "--idea", "_fixture", *extra]) == 2
    assert needle in capsys.readouterr().err
    assert research(root, "nb_ask") == []


@pytest.mark.parametrize(
    ("content", "needle"), [("{not json", "is not valid JSON"), ("[1, 2]", "a JSON object")]
)
def test_ask_refuses_a_schema_that_is_not_a_json_object(root, tmp_path, capsys, content, needle):
    schema = tmp_path / "schema.json"
    schema.write_text(content, encoding="utf-8")
    assert main([*ASK, "--schema", str(schema)]) == 2
    assert needle in capsys.readouterr().err


def test_ask_dry_run_answers_from_the_fixture_reads_no_key_and_logs_nothing(
    root, capsys, no_secrets
):
    log = root / "ideas/_fixture/costs.jsonl"
    before = log.read_text(encoding="utf-8")
    assert main([*ASK, "--dry-run"]) == 0
    [path] = research(root, "nb_ask")
    assert path.name.endswith(".dryrun.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["dry_run"] is True and data["answer"] == fixture("neuralbox/respond")["answer"]
    assert log.read_text(encoding="utf-8") == before
    [report] = capsys.readouterr().err.splitlines()
    assert report.startswith("nb_ask: dry run: wrote ideas/_fixture/research/nb_ask_")
    assert report.endswith("not logged")


def test_a_run_neuralbox_reports_failed_is_logged_and_writes_nothing(root, capsys, monkeypatch):
    wire(monkeypatch, reply(answer="Error: Query timed out", errors=["Query timed out (540s)"]))
    assert main(ASK) == 1
    assert research(root, "nb_ask") == []
    line = costs.read_lines("_fixture")[-1]
    assert (line["kind"], line["ref"], line["amount_eur"]) == ("llm", "req-1", 0.23)
    err = capsys.readouterr().err
    assert "nb: neuralbox: the run failed: Query timed out (540s)" in err
    assert "0.23 EUR (nb ask, 0.25 USD) logged before the failure" in err


def test_a_cost_neuralbox_does_not_report_is_logged_as_planned(root, monkeypatch):
    wire(monkeypatch, reply(cost_usd=None))
    assert main(ASK) == 0
    line = costs.read_lines("_fixture")[-1]
    assert line["amount_eur"] == nb.PLANNED_EUR == 0.5
    assert line["note"] == "nb ask, cost not reported: the planned 0.5 EUR"


def test_a_call_neuralbox_refuses_costs_nothing(root, capsys, monkeypatch):
    log = root / "ideas/_fixture/costs.jsonl"
    before = log.read_text(encoding="utf-8")
    wire(monkeypatch, httpx.Response(403, json={"error": "Email domain not allowed"}))
    assert main(ASK) == 1
    assert log.read_text(encoding="utf-8") == before and research(root, "nb_ask") == []
    [err] = capsys.readouterr().err.splitlines()
    assert err == 'nb: neuralbox: HTTP 403: POST /respond: {"error":"Email domain not allowed"}'


def test_an_unknown_idea_is_refused_before_any_key_or_call(root, capsys, monkeypatch):
    monkeypatch.setattr(neuralbox, "client", lambda dry_run=False: pytest.fail("client built"))
    assert main(["nb", "ask", "--idea", "nope", "--prompt", "hi"]) == 1
    err = capsys.readouterr().err
    assert err.startswith("nb: no idea 'nope' in ideas/") and err.count("\n") == 1


@pytest.mark.parametrize("argv", [ASK, ADSINSIGHTS], ids=["ask", "adsinsights"])
def test_a_real_run_without_the_master_key_stops_on_one_line(root, capsys, argv):
    assert main(argv) == 1
    out, err = capsys.readouterr()
    assert out == "" and "make secrets-init" in err and err.count("\n") == 1
    assert research(root, "nb_") == []


# --- nb adsinsights ----------------------------------------------------------------------------


def test_adsinsights_asks_for_the_aggregations_with_the_whitelist_and_the_schema(root, monkeypatch):
    seen = wire(monkeypatch, reply(structured_output=STRUCTURED))
    assert main(ADSINSIGHTS) == 0
    body = body_of(seen[0])
    assert body["allowed_tools"] == WHITELIST
    assert body["output_format"] == {"type": "json_schema", "schema": nb.ADSINSIGHTS_SCHEMA}
    assert body["max_turns"] == 8  # two networks
    prompt = body["prompt"]
    for needle in [
        '"home security"',
        "LookupAdsInsights",
        "ListCategories",
        'section="aggregations"',
        'tile="company"',
        'sort="all"',
        'countries=["FR", "US"]',
        "top=10",
        'section="copy"',
        "facebook, search",
    ]:
        assert needle in prompt, needle
    assert prompt.endswith(neuralbox.DISCIPLINE)
    [path] = research(root, "nb_adsinsights")
    assert json.loads(path.read_text(encoding="utf-8")) == STRUCTURED


def test_adsinsights_passes_the_networks_and_top_asked(root, monkeypatch):
    seen = wire(monkeypatch, reply(structured_output=STRUCTURED))
    networks = "facebook,tiktok,snapchat,native,linkedin,search"
    assert main([*ADSINSIGHTS, "--networks", networks, "--top", "56"]) == 0
    body = body_of(seen[0])
    assert "facebook, tiktok, snapchat, native, linkedin, search" in body["prompt"]
    assert "top=56" in body["prompt"]
    assert body["max_turns"] == 16  # a lookup and two queries per network, with room to answer


def test_adsinsights_keeps_only_what_the_schema_describes(root, monkeypatch):
    structured = copy.deepcopy(STRUCTURED)
    structured["rows"] = [{"name": "RAW-ROW", "reach": 1}]
    structured["networks"][0]["raw"] = {"cards": ["RAW-CARD"]}
    structured["networks"][0]["top_companies"][0]["page_id"] = "RAW-ID"
    structured["networks"][1]["top_companies"] = "RAW-TEXT"  # not a list
    calls = [{"name": WHITELIST[2], "input": {}, "output": "RAW-OUTPUT"}]
    answer = reply(
        structured_output=structured,
        answer="RAW-ANSWER",
        explanation="RAW-TEXT",
        tools_called=calls,
    )
    wire(monkeypatch, answer)
    assert main(ADSINSIGHTS) == 0
    [path] = research(root, "nb_adsinsights")
    text = path.read_text(encoding="utf-8")
    assert "RAW" not in text
    kept = json.loads(text)
    assert kept["networks"][1]["top_companies"] == []
    assert kept["networks"][0]["top_companies"][0] == {"name": "Alarmo Example", "share_pct": 12.7}


def test_adsinsights_without_structured_output_is_logged_and_writes_nothing(
    root, capsys, monkeypatch
):
    wire(monkeypatch, reply(answer="I could not finish", structured_output=None, cost_usd=0.3))
    assert main(ADSINSIGHTS) == 1
    assert research(root, "nb_adsinsights") == []
    line = costs.read_lines("_fixture")[-1]
    assert (line["kind"], line["amount_eur"], line["note"]) == (
        "llm",
        0.276,
        "nb adsinsights, 0.3 USD",
    )
    assert "nb: neuralbox: no structured output: the answer is not kept" in capsys.readouterr().err


def test_adsinsights_summary_is_one_row_per_network(root, capsys, monkeypatch):
    wire(monkeypatch, reply(structured_output=STRUCTURED))
    assert main(ADSINSIGHTS) == 0
    out = capsys.readouterr().out
    assert out == (
        "Home Security in FR, US\n"
        "network   total_reach  advertisers  top companies\n"
        "--------  -----------  -----------  ------------------------------------------\n"
        "facebook  24,500,000   312          Alarmo Example 12.7%, Securis Example 8.1%\n"
        "search\n"
        "typical hooks: free installation; 24/7 monitoring\n"
        "caveats:\n"
        "  facebook: reach is per network\n"
        "  search: QueryAdsInsights failed: timeout\n"
    )


def test_adsinsights_summary_when_no_category_matches(root, capsys, monkeypatch):
    not_found = {
        "category_resolved": "",
        "countries": ["FR"],
        "networks": [],
        "typical_hooks": [],
        "not_found": True,
    }
    wire(monkeypatch, reply(structured_output=not_found))
    assert main([*ADSINSIGHTS[:-1], "FR"]) == 0
    assert capsys.readouterr().out == 'no AdsInsights category matches "home security" (FR)\n'


@pytest.mark.parametrize(
    ("extra", "needle"),
    [
        (["--countries", "FR"], "--category"),
        (["--category", "  ", "--countries", "FR"], "--category"),
        (["--category", "x"], "--countries"),
        (["--category", "x", "--countries", "France"], "'France' is not a country code"),
        (["--category", "x", "--countries", ","], "--countries"),
        (["--category", "x", "--countries", "FR", "--networks", "bing"], "unknown network 'bing'"),
        (["--category", "x", "--countries", "FR", "--top", "0"], "is not from 1 to 56"),
        (["--category", "x", "--countries", "FR", "--top", "57"], "is not from 1 to 56"),
    ],
)
def test_adsinsights_refuses_a_command_line_it_cannot_run(root, capsys, monkeypatch, extra, needle):
    monkeypatch.setattr(neuralbox, "client", lambda dry_run=False: pytest.fail("client built"))
    assert main(["nb", "adsinsights", "--idea", "_fixture", *extra]) == 2
    assert needle in capsys.readouterr().err


def test_adsinsights_reads_regions_and_lowercase_codes(root, monkeypatch):
    seen = wire(monkeypatch, reply(structured_output=STRUCTURED))
    argv = ["nb", "adsinsights", "--idea", "_fixture", "--category", "x"]
    assert main([*argv, "--countries", "fr, emea,fr", "--networks", "Search"]) == 0
    prompt = body_of(seen[0])["prompt"]
    assert 'countries=["FR", "EMEA"]' in prompt and "in search." in prompt


def test_adsinsights_dry_run_answers_from_the_fixture_and_logs_nothing(root, capsys, no_secrets):
    log = root / "ideas/_fixture/costs.jsonl"
    before = log.read_text(encoding="utf-8")
    assert main([*ADSINSIGHTS, "--dry-run"]) == 0
    [path] = research(root, "nb_adsinsights")
    assert path.name.endswith(".dryrun.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    structured = fixture("neuralbox/adsinsights")["structured_output"]
    assert data == {"dry_run": True, **structured}
    assert log.read_text(encoding="utf-8") == before
    out, err = capsys.readouterr()
    assert out.startswith(f"{structured['category_resolved']} in ")
    [report] = err.splitlines()
    assert report.startswith("nb_adsinsights: dry run: wrote ideas/_fixture/research/")
    assert report.endswith("not logged")


# --- the selftest ------------------------------------------------------------------------------


@pytest.mark.parametrize("action", ["ask", "adsinsights"])
def test_the_selftest_is_a_heartbeat_and_one_pong(root, capsys, monkeypatch, action):
    log = root / "ideas/_fixture/costs.jsonl"
    before = log.read_text(encoding="utf-8")
    seen = wire(monkeypatch, heartbeat("Read", *WHITELIST), reply(answer="pong", cost_usd=0.02))
    assert main(["nb", action, "--selftest"]) == 0
    assert capsys.readouterr().out == "OK neuralbox 4 items; respond cost 0.0184 EUR\n"
    assert [(r.method, r.url.path) for r in seen] == [("GET", "/heartbeat"), ("POST", "/respond")]
    body = body_of(seen[1])
    assert body["prompt"] == "Reply with the single word pong" + neuralbox.DISCIPLINE
    assert body["max_turns"] == 1 and "allowed_tools" not in body
    assert research(root, "nb_") == [] and log.read_text(encoding="utf-8") == before


def test_the_adsinsights_selftest_needs_the_whitelisted_tools(root, capsys, monkeypatch):
    seen = wire(monkeypatch, heartbeat("Read", WHITELIST[0]))
    assert main(["nb", "adsinsights", "--selftest"]) == 1
    [err] = capsys.readouterr().err.splitlines()
    assert err == (
        "nb: neuralbox: the heartbeat lists no mcp__tools__ListCategories, "
        "mcp__tools__QueryAdsInsights"
    )
    assert len(seen) == 1  # no paid call


def test_a_selftest_neuralbox_answers_with_errors_fails(root, capsys, monkeypatch):
    wire(monkeypatch, heartbeat("Read"), reply(answer="", errors=["Claude returned an error"]))
    assert main(["nb", "ask", "--selftest"]) == 1
    assert "nb: neuralbox: the run failed: Claude returned an error" in capsys.readouterr().err


def test_a_selftest_without_an_answer_fails(root, capsys, monkeypatch):
    wire(monkeypatch, heartbeat("Read"), reply(answer=" "))
    assert main(["nb", "ask", "--selftest"]) == 1
    assert "nb: neuralbox: the selftest's respond call came back without an answer" in (
        capsys.readouterr().err
    )


@pytest.mark.parametrize("action", ["ask", "adsinsights"])
def test_a_selftest_dry_run_answers_from_the_fixtures(root, capsys, no_secrets, action):
    assert main(["nb", action, "--selftest", "--dry-run"]) == 0
    cost = fixture("neuralbox/respond")["cost_usd"] * costs.USD_EUR
    assert capsys.readouterr().out == f"OK neuralbox 10 items; respond cost {cost:.4f} EUR\n"


# --- the command -------------------------------------------------------------------------------


def test_nb_is_registered_with_its_two_actions(capsys):
    assert main(["--help"]) == 0
    assert "nb" in capsys.readouterr().out
    assert main(["nb", "--help"]) == 0
    out = capsys.readouterr().out
    assert "ask" in out and "adsinsights" in out
