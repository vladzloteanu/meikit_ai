import functools
import json
import socket
import subprocess
import sys
import types
from datetime import date

import httpx
import pytest

from factory import cli, secrets, toolbase, vercel
from factory.cli import main
from factory.http import Client, ProviderError
from factory.providers import arcticshift, neuralbox
from factory.tools import doctor
from factory.tools.doctor import Proc

TOKEN = "vercel-test-token-0123456789"
USER = {"username": "octo", "plan": "pro", "northstar": False}
NORTHSTAR = {"username": "octo", "plan": "hobby", "northstar": True}
ACCOUNT = {
    "account": {"current_month_usage": 10, "monthly_allowance": 100, "remaining_credits": 90},
    "subscription": {"period_start": "2026-10-05T14:01:59Z", "period_end": "2026-11-05T14:01:59Z"},
}
USED_UP = {
    "account": {
        "current_month_usage": 100005,
        "monthly_allowance": 100000,
        "remaining_credits": -5,
    },
    "subscription": {"period_start": "2026-10-05T14:01:59Z", "period_end": "2026-11-05T14:01:59Z"},
}
QUOTA_BODY = "You have used all of the searches for the month. Please upgrade your plan."
HEARTBEAT = {"status": "ok", "available_tools": [*neuralbox.WHITELIST, "Read", "mcp__x__y"]}
POSTS = [{"id": f"post_{n:02}"} for n in range(1, 8)]
SECRETS = {
    "providers.searchapi.api_key",
    "providers.seranking.api_token",
    "providers.firecrawl.api_key",
    "accounts.meta.ad_account_id",
    "accounts.google_ads.customer_id",
    "accounts.stripe.secret_key",
    "accounts.sending_domain.domain",
    "accounts.resend.account_key",
    "accounts.turnstile.site_key",
}
NO_ASSETS = {path for path in SECRETS if path.startswith("providers.")}
COMMANDS = {
    "vercel": Proc(0, "octo\n", "Vercel CLI 63.1.2\n"),
    "gh": Proc(0, "github.com\n  ✓ Logged in to github.com account octo (keyring)\n", ""),
    "dig": Proc(0, "76.76.21.21\n", ""),
}
NETWORK = {"searchapi", "heartbeat", "arcticshift", "rdap", "vercel_scope", "vercel_user"}
HUMAN = ["reddit_reply", "reddit_post", "linkedin_outreach", "community_post"]
ALL_RECIPES = [
    "fake-door-saas",
    "pre-order",
    "concierge-b2b",
    "cold-email-b2b",
    "complaint-response",
    "waitlist-b2c",
]


def slow_down(reset: str | None = "7") -> arcticshift.SlowDown:
    """Arctic Shift's throttle: a 422 "slow down" answered at once, its wait in
    X-RateLimit-Reset."""
    headers = {"X-RateLimit-Reset": reset} if reset is not None else {}
    request = httpx.Request("GET", "https://arctic-shift.photon-reddit.com/api/posts/search")
    response = httpx.Response(
        422, text="Timeout. Maybe slow down a bit", headers=headers, request=request
    )
    return arcticshift.SlowDown(response)


class FakeCtx:
    """A machine where every check passes, unless a test says otherwise.

    An answer is a value to return or an exception to raise; `arctic` is a list, one answer per
    search. `calls` records what the checks asked for, `slept` the waits.
    """

    def __init__(
        self,
        *,
        offline=False,
        present=SECRETS,
        secrets_error=None,
        commands=None,
        searchapi=ACCOUNT,
        heartbeat=HEARTBEAT,
        arctic=None,
        rdap="taken",
        scope=("personal", None),
        user=USER,
        selftests=None,
    ):
        self.offline = offline
        self.present = present
        self.secrets_error = secrets_error
        self.commands = {**COMMANDS, **(commands or {})}
        self.answers = {
            "searchapi": searchapi,
            "heartbeat": heartbeat,
            "rdap": rdap,
            "vercel_scope": scope,
            "vercel_user": user,
        }
        self.arctic = list(arctic) if arctic is not None else [POSTS]
        self.selftests = selftests or {}
        self.calls = []
        self.slept = []

    def _give(self, name):
        self.calls.append(name)
        answer = self.answers[name]
        if isinstance(answer, BaseException):
            raise answer
        return answer

    def load_secrets(self):
        self.calls.append("load_secrets")
        if self.secrets_error:
            raise self.secrets_error

    def has_secret(self, dotpath):
        if self.secrets_error:
            raise self.secrets_error
        return dotpath in self.present

    def command(self, argv):
        self.calls.append(" ".join(argv))
        return self.commands[argv[0]]

    def searchapi_account(self):
        return self._give("searchapi")

    def nb_heartbeat(self):
        return self._give("heartbeat")

    def arcticshift_posts(self):
        self.calls.append("arcticshift")
        answer = self.arctic.pop(0)
        if isinstance(answer, BaseException):
            raise answer
        return answer

    def sleep(self, seconds):
        self.slept.append(seconds)

    def rdap_status(self, domain):
        assert domain == "meikit.ai"
        return self._give("rdap")

    def vercel_scope(self):
        return self._give("vercel_scope")

    def vercel_user(self):
        return self._give("vercel_user")

    def selftest(self, argv):
        self.calls.append(" ".join(argv))
        return self.selftests.get(argv[0], Proc(0, f"OK {argv[0]} 3 items\n", ""))


def check(name, ctx):
    """The result of the check `name` on `ctx`."""
    (found,) = [c for c in doctor.CHECKS + doctor.LIVE_CHECKS if c.name == name]
    return found.fn(ctx)


def result(level, detail):
    return doctor.Result(ok=level == "ok", level=level, detail=detail)


@pytest.fixture
def use(monkeypatch):
    """Make `factory doctor` run its checks on the given fake machine."""

    def install(fake):
        def make(offline=False):
            fake.offline = offline
            return fake

        monkeypatch.setattr(doctor, "Ctx", make)
        return fake

    return install


@pytest.fixture(autouse=True)
def vercel_dir(tmp_path_factory, monkeypatch):
    """An empty Vercel CLI folder: no test reads the machine's own login."""
    path = tmp_path_factory.mktemp("com.vercel.cli")
    monkeypatch.setattr(vercel, "CONFIG_DIR", path)
    return path


def write_vercel(folder, auth=None, config=None):
    if auth is not None:
        (folder / "auth.json").write_text(json.dumps(auth))
    if config is not None:
        (folder / "config.json").write_text(json.dumps(config))


# --- the checks ---------------------------------------------------------------------------------


def test_the_checks_run_in_the_briefs_order():
    assert [c.name for c in doctor.CHECKS] == [
        "secrets.master_key",
        "secrets.providers",
        "nb.heartbeat",
        "provider.arcticshift",
        "vercel.login",
        "vercel.scope",
        "vercel.plan",
        "gh.auth",
        "domain.meikit",
        "assets.meta",
        "assets.google_ads",
        "assets.stripe",
        "assets.sending_domain",
        "assets.resend",
        "assets.turnstile",
    ]
    offline = {c.name for c in doctor.CHECKS if not c.needs_network}
    assert offline == {"secrets.master_key", "secrets.providers"} | {
        c.name for c in doctor.CHECKS if c.name.startswith("assets.")
    }
    assert all(c.blocks for c in doctor.CHECKS + doctor.LIVE_CHECKS)


def test_a_healthy_machine_passes_every_check():
    results = doctor.run_checks(doctor.CHECKS, FakeCtx())
    assert {name: r.level for name, r in results.items() if not r.ok} == {}
    assert list(results) == [c.name for c in doctor.CHECKS]


def test_the_master_key_check_reports_what_the_secrets_say():
    assert check("secrets.master_key", FakeCtx()).level == "ok"
    missing = secrets.SecretsUnavailable("no secrets/master.key: run `make secrets-init`")
    assert check("secrets.master_key", FakeCtx(secrets_error=missing)) == result(
        "fail", "no secrets/master.key: run `make secrets-init`"
    )


def test_a_missing_provider_key_fails_naming_its_dotpath():
    present = SECRETS - {"providers.firecrawl.api_key", "providers.seranking.api_token"}
    found = check("secrets.providers", FakeCtx(present=present))
    assert found.level == "fail"
    assert "providers.seranking.api_token, providers.firecrawl.api_key" in found.detail
    unreadable = FakeCtx(secrets_error=secrets.SecretsUnavailable("no key"))
    assert check("secrets.providers", unreadable).level == "fail"


def test_provider_keys_offline_are_presence_only():
    ctx = FakeCtx(offline=True)
    assert check("secrets.providers", ctx) == result(
        "ok", "searchapi, seranking and firecrawl keys present"
    )
    assert "searchapi" not in ctx.calls


def test_the_searchapi_quota_left_is_ok_with_the_count():
    found = check("secrets.providers", FakeCtx())
    assert found == result(
        "ok",
        "searchapi, seranking and firecrawl keys present; SearchAPI: 90 of 100 searches left "
        "this month",
    )


def test_a_used_up_searchapi_quota_fails_with_its_reset_date():
    assert check("secrets.providers", FakeCtx(searchapi=USED_UP)) == result(
        "fail",
        "SearchAPI monthly quota used up (resets 2026-11-05); serp_ads and ad_library are blocked",
    )


def test_a_searchapi_quota_429_fails_without_a_date():
    error = ProviderError("searchapi", 429, f"GET /api/v1/me?api_key=***: {QUOTA_BODY}")
    assert check("secrets.providers", FakeCtx(searchapi=error)) == result(
        "fail", "SearchAPI monthly quota used up; serp_ads and ad_library are blocked"
    )


@pytest.mark.parametrize(
    "error",
    [
        ProviderError("searchapi", 503, "GET /api/v1/me?api_key=***: Service Unavailable"),
        ProviderError("searchapi", 429, "GET /api/v1/me?api_key=***: too many requests"),
        ProviderError("searchapi", None, "GET /api/v1/me: ConnectError: refused"),
    ],
    ids=["5xx", "rate-limit", "network"],
)
def test_a_searchapi_outage_is_a_warning(error):
    found = check("secrets.providers", FakeCtx(searchapi=error))
    assert found.level == "warn"
    assert found.detail.startswith("searchapi, seranking and firecrawl keys present; SearchAPI ")
    assert str(error) in found.detail


def test_searchapi_refusing_the_key_fails():
    error = ProviderError("searchapi", 401, 'GET /api/v1/me?api_key=***: {"error": "Invalid key"}')
    found = check("secrets.providers", FakeCtx(searchapi=error))
    assert found.level == "fail" and "HTTP 401" in found.detail


def test_a_searchapi_answer_without_a_quota_is_a_warning():
    found = check("secrets.providers", FakeCtx(searchapi={"account": {}}))
    assert found.level == "warn" and "remaining_credits" in found.detail


def test_the_nb_heartbeat_gives_the_tool_count():
    assert check("nb.heartbeat", FakeCtx()) == result(
        "ok", "NeuralBox up: 5 tools, the AdsInsights ones included"
    )


def test_an_unreachable_neuralbox_is_a_warning():
    error = ProviderError("neuralbox", None, "GET /heartbeat: ConnectError: refused")
    assert check("nb.heartbeat", FakeCtx(heartbeat=error)) == result(
        "warn", f"NeuralBox unreachable: {error}"
    )


def test_a_neuralbox_without_the_adsinsights_tools_is_a_warning():
    found = check("nb.heartbeat", FakeCtx(heartbeat={"available_tools": ["Read"]}))
    assert found == result(
        "warn",
        "NeuralBox up: 1 tool, but not mcp__tools__LookupAdsInsights, mcp__tools__ListCategories, "
        "mcp__tools__QueryAdsInsights: nb adsinsights is blocked",
    )


def test_arctic_shift_answers_a_30_day_search():
    ctx = FakeCtx()
    assert check("provider.arcticshift", ctx) == result("ok", "30-day posts search: 7 posts")
    assert ctx.calls == ["arcticshift"] and ctx.slept == []


def test_an_arctic_shift_throttle_is_waited_out_once():
    ctx = FakeCtx(arctic=[slow_down("7"), POSTS])
    assert check("provider.arcticshift", ctx) == result(
        "ok", "30-day posts search: 7 posts, after a 7 s throttle"
    )
    assert ctx.slept == [7.0] and ctx.calls == ["arcticshift", "arcticshift"]


@pytest.mark.parametrize(("reset", "waited"), [("600", 60.0), (None, 3.0)])
def test_the_arctic_shift_wait_is_capped_and_defaulted(reset, waited):
    ctx = FakeCtx(arctic=[slow_down(reset), POSTS])
    assert check("provider.arcticshift", ctx).level == "ok"
    assert ctx.slept == [waited]


def test_arctic_shift_refusing_again_warns_throttled():
    ctx = FakeCtx(arctic=[slow_down("5"), slow_down("5")])
    found = check("provider.arcticshift", ctx)
    assert found.level == "warn" and found.detail.startswith("throttled")
    assert ctx.slept == [5.0] and len(ctx.calls) == 2


@pytest.mark.parametrize(
    "answers",
    [
        [ProviderError("arcticshift", 503, "GET /api/posts/search: down")],
        [slow_down(), ProviderError("arcticshift", None, "GET /api/posts/search: timeout")],
    ],
    ids=["down", "down-after-throttle"],
)
def test_arctic_shift_never_fails_the_doctor(answers):
    found = check("provider.arcticshift", FakeCtx(arctic=answers))
    assert found.level == "warn" and "Arctic Shift did not answer" in found.detail


def test_vercel_login_names_the_user():
    ctx = FakeCtx()
    assert check("vercel.login", ctx) == result("ok", "logged in as octo")
    assert ctx.calls == ["vercel whoami"]


@pytest.mark.parametrize(
    ("proc", "detail"),
    [
        (
            Proc(1, "", "Vercel CLI 63.1.2\nError: No existing credentials found.\n"),
            "`vercel whoami` failed: Error: No existing credentials found.; run `vercel login`",
        ),
        (Proc(None, "", "vercel is not installed"), "vercel is not installed"),
    ],
    ids=["logged-out", "no-cli"],
)
def test_vercel_login_fails_when_whoami_does(proc, detail):
    assert check("vercel.login", FakeCtx(commands={"vercel": proc})) == result("fail", detail)


def test_the_personal_vercel_scope_is_ok():
    assert check("vercel.scope", FakeCtx()) == result("ok", "personal scope (octo)")


def test_a_team_scope_fails_naming_vercel_switch_and_the_username():
    found = check("vercel.scope", FakeCtx(scope=("team", "acme-product")))
    assert found == result(
        "fail", "CLI scope is team acme-product, not personal: run `vercel switch octo`"
    )


def test_a_northstar_account_fails_saying_vercel_switch_is_refused():
    found = check("vercel.scope", FakeCtx(scope=("team", "acme-product"), user=NORTHSTAR))
    assert found == result(
        "fail",
        "CLI scope is team acme-product: octo is a team-based (northstar) account, which has no "
        "personal scope and refuses `vercel switch octo`; see docs/doctor.md",
    )


def test_a_northstar_account_without_a_current_team_still_fails():
    # Its CLI then works in the account's default team, which may be anyone's.
    found = check("vercel.scope", FakeCtx(user=NORTHSTAR))
    assert found.level == "fail"
    assert found.detail.startswith("the CLI works in the account's default team: octo is a ")


def test_an_unreadable_vercel_account_fails_the_scope():
    error = vercel.VercelError("the Vercel CLI is not logged in: run `vercel login`")
    assert check("vercel.scope", FakeCtx(scope=("team", "acme-product"), user=error)) == result(
        "fail",
        "CLI scope is team acme-product, not personal: run `vercel switch <username>` "
        "(the Vercel CLI is not logged in: run `vercel login`)",
    )
    found = check("vercel.scope", FakeCtx(user=error))
    assert found.level == "fail" and "unconfirmed" in found.detail


@pytest.mark.parametrize(
    ("user", "expected"),
    [
        (
            NORTHSTAR,
            result(
                "warn", "Hobby forbids commercial use; upgrade to Pro before the first paid traffic"
            ),
        ),
        (USER, result("ok", "pro plan")),
        ({**USER, "plan": None}, result("warn", "GET /v2/user gives no plan")),
        (
            vercel.VercelError("GET /v2/user: HTTP 403 (forbidden)"),
            result("warn", "the plan cannot be read: GET /v2/user: HTTP 403 (forbidden)"),
        ),
    ],
    ids=["hobby", "pro", "no-plan", "unreadable"],
)
def test_the_vercel_plan(user, expected):
    assert check("vercel.plan", FakeCtx(user=user)) == expected


def test_gh_auth_names_the_account():
    ctx = FakeCtx()
    assert check("gh.auth", ctx) == result("ok", "logged in to github.com as octo")
    assert ctx.calls == ["gh auth status"]


@pytest.mark.parametrize(
    ("proc", "detail"),
    [
        (
            Proc(
                1, "", "You are not logged into any GitHub hosts. To log in, run: gh auth login\n"
            ),
            "`gh auth status` failed (exit 1): run `gh auth login`",
        ),
        (Proc(None, "", "gh is not installed"), "gh is not installed"),
    ],
    ids=["logged-out", "no-cli"],
)
def test_gh_auth_fails_when_gh_cannot_create_repos(proc, detail):
    assert check("gh.auth", FakeCtx(commands={"gh": proc})) == result("fail", detail)


def test_a_free_lab_domain_warns_with_the_setup_step():
    ctx = FakeCtx(rdap="available")
    assert check("domain.meikit", ctx) == result(
        "warn", "lab domain not bought: /factory-setup step 1"
    )
    assert "dig +short meikit.ai" not in ctx.calls


@pytest.mark.parametrize(
    "answer", ["76.76.21.21\n", "cname.vercel-dns.com.\n76.76.21.98\n"], ids=["a", "cname"]
)
def test_a_lab_domain_pointed_at_vercel_is_ok(answer):
    ctx = FakeCtx(commands={"dig": Proc(0, answer, "")})
    assert check("domain.meikit", ctx) == result("ok", "meikit.ai registered and pointed at Vercel")
    assert ctx.calls == ["rdap", "dig +short meikit.ai"]


def test_a_lab_domain_registered_elsewhere_warns_that_its_owner_is_unknown():
    parked = Proc(0, "pixie.porkbun.com.\n207.207.210.229\n", "")
    assert check("domain.meikit", FakeCtx(commands={"dig": parked})) == result(
        "warn", "registered (by whom unknown; confirm with the owner or pick another lab domain)"
    )


@pytest.mark.parametrize(
    ("ctx", "start"),
    [
        (FakeCtx(rdap="unknown"), "RDAP cannot tell whether meikit.ai is registered"),
        (FakeCtx(rdap=ProviderError("rdap", None, "GET /domain/meikit.ai: boom")), "RDAP "),
        (FakeCtx(commands={"dig": Proc(9, ";; no servers could be reached\n", "")}), "registered"),
        (FakeCtx(commands={"dig": Proc(None, "", "dig is not installed")}), "registered"),
    ],
    ids=["rdap-unknown", "rdap-down", "dig-failed", "no-dig"],
)
def test_a_lab_domain_that_cannot_be_read_is_a_warning(ctx, start):
    found = check("domain.meikit", ctx)
    assert found.level == "warn" and found.detail.startswith(start)


ASSETS = [
    ("assets.meta", "accounts.meta.ad_account_id", "meta_feed"),
    ("assets.google_ads", "accounts.google_ads.customer_id", "google_search"),
    ("assets.stripe", "accounts.stripe.secret_key", "pre-order"),
    ("assets.sending_domain", "accounts.sending_domain.domain", "cold_email_b2b"),
    ("assets.resend", "accounts.resend.account_key", "the stand's email sending"),
    ("assets.turnstile", "accounts.turnstile.site_key", "the stand's anti-bot check"),
]


@pytest.mark.parametrize(("name", "dotpath", "unlocks"), ASSETS, ids=[a[0] for a in ASSETS])
def test_an_asset_warns_when_empty_and_names_what_it_unlocks(name, dotpath, unlocks):
    assert check(name, FakeCtx(present=SECRETS - {dotpath})) == result(
        "warn", f"{dotpath} not set: {unlocks} stays locked (/factory-setup)"
    )
    assert check(name, FakeCtx()) == result("ok", f"{dotpath} set: unlocks {unlocks}")
    assert [c.blocks for c in doctor.CHECKS if c.name == name] == [unlocks]


def test_an_asset_is_a_warning_when_the_secrets_cannot_be_read():
    ctx = FakeCtx(secrets_error=secrets.SecretsUnavailable("no key"))
    found = check("assets.meta", ctx)
    assert found.level == "warn" and "the secrets cannot be read" in found.detail


# --- eligibility --------------------------------------------------------------------------------


def results_with(*ok_assets):
    """Results where only the named asset checks passed."""
    return {name: result("ok" if name in ok_assets else "warn", "") for name, _, _ in ASSETS}


def test_without_assets_only_the_human_channels_are_eligible():
    assert doctor.eligible_channels(results_with()) == HUMAN
    assert doctor.eligible_channels({}) == HUMAN


def test_each_paid_channel_needs_its_asset():
    assert doctor.eligible_channels(results_with("assets.meta")) == [*HUMAN, "meta_feed"]
    assert doctor.eligible_channels(results_with("assets.google_ads")) == [*HUMAN, "google_search"]
    assert doctor.eligible_channels(
        results_with("assets.meta", "assets.google_ads", "assets.sending_domain")
    ) == [*HUMAN, "google_search", "meta_feed", "cold_email_b2b"]


def test_pre_order_needs_stripe():
    assert doctor.eligible_recipes(results_with()) == [r for r in ALL_RECIPES if r != "pre-order"]
    assert doctor.eligible_recipes(results_with("assets.stripe")) == ALL_RECIPES


# --- the command --------------------------------------------------------------------------------


def test_doctor_prints_the_table_and_the_eligible_sets(use, capsys):
    use(FakeCtx(present=NO_ASSETS))
    assert main(["doctor"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].split() == ["check", "level", "detail"]
    assert set(lines[1]) == {"-", " "}
    assert lines[2].split()[:2] == ["secrets.master_key", "ok"]
    assert lines[11].split()[:2] == ["assets.meta", "warn"]
    assert len(lines) == 2 + len(doctor.CHECKS) + 2
    assert lines[-2] == f"eligible channels: {', '.join(HUMAN)}"
    assert lines[-1] == (
        "eligible recipes: fake-door-saas, concierge-b2b, cold-email-b2b, complaint-response, "
        "waitlist-b2c"
    )


def test_doctor_exits_1_when_a_check_fails(use, capsys):
    use(FakeCtx(scope=("team", "acme-product")))
    assert main(["doctor"]) == 1
    assert "`vercel switch octo`" in capsys.readouterr().out


def test_doctor_json_has_the_checks_and_the_eligible_sets(use, capsys):
    use(FakeCtx(present=SECRETS - {"accounts.meta.ad_account_id"}, user=NORTHSTAR))
    assert main(["doctor", "--json"]) == 1
    data = json.loads(capsys.readouterr().out)
    assert list(data) == ["checks", "eligible_channels", "eligible_recipes"]
    assert [c["name"] for c in data["checks"]] == [c.name for c in doctor.CHECKS]
    assert data["checks"][9] == {
        "name": "assets.meta",
        "level": "warn",
        "ok": False,
        "detail": "accounts.meta.ad_account_id not set: meta_feed stays locked (/factory-setup)",
        "blocks": "meta_feed",
    }
    assert {c["name"]: c["level"] for c in data["checks"] if c["level"] != "ok"} == {
        "vercel.scope": "fail",
        "vercel.plan": "warn",
        "assets.meta": "warn",
    }
    assert data["eligible_channels"] == [*HUMAN, "google_search", "cold_email_b2b"]
    assert data["eligible_recipes"] == ALL_RECIPES


def test_doctor_offline_skips_the_network_checks(use, capsys):
    fake = use(FakeCtx())
    assert main(["doctor", "--offline", "--json"]) == 0
    checks = json.loads(capsys.readouterr().out)["checks"]
    skipped = [c["name"] for c in checks if c["level"] == "skip"]
    assert skipped == [c.name for c in doctor.CHECKS if c.needs_network]
    assert {c["detail"] for c in checks if c["level"] == "skip"} == {
        "skipped: needs the network (run without --offline)"
    }
    assert fake.calls == ["load_secrets"]  # no API, no CLI: only the secrets were read


def test_doctor_live_runs_each_providers_selftest_in_process(use, capsys):
    fake = use(FakeCtx())
    assert main(["doctor", "--live", "--json"]) == 0
    checks = json.loads(capsys.readouterr().out)["checks"]
    assert [c["name"] for c in checks] == [c.name for c in doctor.CHECKS + doctor.LIVE_CHECKS]
    assert [c["name"] for c in checks[len(doctor.CHECKS) :]] == [
        "selftest.searchapi",
        "selftest.seranking",
        "selftest.firecrawl",
        "selftest.neuralbox",
        "selftest.arcticshift",
        "selftest.algolia",
        "selftest.rdap",
    ]
    assert [call for call in fake.calls if call.endswith("--selftest")] == [
        "serp_ads --selftest",
        "keyword_volume --selftest",
        "pricing_scan --selftest",
        "nb adsinsights --selftest",
        "reddit_mentions --selftest",
        "hn_mentions --selftest",
        "domain_check --selftest",
    ]
    assert checks[len(doctor.CHECKS)]["detail"] == "OK serp_ads 3 items"


def test_a_failed_selftest_fails_for_a_keyed_provider_and_warns_for_a_free_one(use, capsys):
    refused = Proc(1, "", "serp_ads: searchapi: HTTP 429: used all of the searches\n")
    throttled = Proc(1, "", "reddit_mentions: arcticshift: HTTP 422: slow down\n")
    use(FakeCtx(selftests={"serp_ads": refused, "reddit_mentions": throttled}))
    assert main(["doctor", "--live", "--json"]) == 1
    checks = {c["name"]: c for c in json.loads(capsys.readouterr().out)["checks"]}
    assert checks["selftest.searchapi"]["level"] == "fail"
    assert checks["selftest.searchapi"]["detail"] == (
        "serp_ads: searchapi: HTTP 429: used all of the searches"
    )
    assert checks["selftest.arcticshift"]["level"] == "warn"
    assert checks["selftest.neuralbox"]["level"] == "ok"


def test_offline_and_live_cannot_go_together(capsys):
    assert main(["doctor", "--offline", "--live"]) == 2
    assert "not allowed with argument" in capsys.readouterr().err


# --- the real machine: Ctx and factory.vercel ---------------------------------------------------


def test_the_scope_is_personal_without_a_current_team(vercel_dir):
    assert vercel.current_scope() == ("personal", None)  # no config.json at all
    write_vercel(vercel_dir, config={"currentTeam": None, "telemetry": {"enabled": False}})
    assert vercel.current_scope() == ("personal", None)


def test_a_team_scope_is_named_by_its_cached_slug(vercel_dir):
    config = {
        "currentTeam": "team_abc123",
        "cachedTeamSlugs": {"team_abc123": {"slug": "acme-product", "savedAt": 1}},
    }
    write_vercel(vercel_dir, config=config)
    assert vercel.current_scope() == ("team", "acme-product")
    write_vercel(vercel_dir, config={"currentTeam": "team_abc123"})
    assert vercel.current_scope() == ("team", "team_abc123")


def test_cli_auth_reads_the_token_and_the_current_team(vercel_dir):
    assert vercel.cli_auth() is None
    write_vercel(vercel_dir, auth={"// Note": "x", "token": ""})
    assert vercel.cli_auth() is None
    write_vercel(vercel_dir, auth={"token": TOKEN}, config={"currentTeam": "team_abc123"})
    assert vercel.cli_auth() == {"token": TOKEN, "current_team": "team_abc123"}


def serve_vercel(monkeypatch, handler):
    """Make factory.vercel's Client answer from `handler`; return the requests sent."""
    seen = []

    def recording(request):
        seen.append(request)
        return handler(request)

    monkeypatch.setattr(
        vercel, "Client", functools.partial(Client, transport=httpx.MockTransport(recording))
    )
    return seen


def test_user_plan_reads_the_account_with_the_cli_token(vercel_dir, monkeypatch):
    write_vercel(vercel_dir, auth={"token": TOKEN})
    user = {"username": "octo", "version": "northstar", "billing": {"plan": "hobby"}}
    seen = serve_vercel(monkeypatch, lambda req: httpx.Response(200, json={"user": user}))
    assert vercel.user_plan() == {"username": "octo", "plan": "hobby", "northstar": True}
    (request,) = seen
    assert (request.method, str(request.url)) == ("GET", "https://api.vercel.com/v2/user")
    assert request.headers["Authorization"] == f"Bearer {TOKEN}"


def test_a_refused_user_call_names_the_status_and_never_the_token(vercel_dir, monkeypatch):
    write_vercel(vercel_dir, auth={"token": TOKEN})
    body = {"error": {"code": "forbidden", "message": f"Not authorized: {TOKEN}"}}
    serve_vercel(monkeypatch, lambda req: httpx.Response(403, json=body))
    with pytest.raises(vercel.VercelError) as caught:
        vercel.user_plan()
    assert str(caught.value) == "GET /v2/user: HTTP 403 (forbidden: Not authorized: ***)"


def test_user_plan_without_a_login_makes_no_call(monkeypatch):
    seen = serve_vercel(monkeypatch, lambda req: httpx.Response(200, json={}))
    with pytest.raises(vercel.VercelError, match="not logged in"):
        vercel.user_plan()
    assert seen == []


def test_the_ctx_reads_the_vercel_account_once(monkeypatch):
    calls = []
    monkeypatch.setattr(vercel, "user_plan", lambda: calls.append(1) or USER)
    ctx = doctor.Ctx()
    assert check("vercel.scope", ctx).level == "ok" and check("vercel.plan", ctx).level == "ok"
    assert calls == [1]


def test_the_ctx_asks_searchapi_for_its_account_once(monkeypatch):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(429, json={"error": QUOTA_BODY})

    monkeypatch.setattr(secrets, "get", lambda dotpath, *a, **k: "sapi-test-key")
    monkeypatch.setattr(
        doctor, "Client", functools.partial(Client, transport=httpx.MockTransport(handler))
    )
    with pytest.raises(ProviderError) as caught:
        doctor.Ctx().searchapi_account()
    assert caught.value.status == 429 and len(seen) == 1  # the used-up quota is not retried
    assert (seen[0].url.path, dict(seen[0].url.params)) == (
        "/api/v1/me",
        {"api_key": "sapi-test-key"},
    )
    assert "sapi-test-key" not in str(caught.value)


def test_the_ctx_probes_make_one_attempt_each_and_send_no_key(monkeypatch):
    seen = []

    def handler(request):
        seen.append(request)
        if request.url.path == "/heartbeat":
            return httpx.Response(200, json=HEARTBEAT)
        if request.url.path == "/api/posts/search":
            return httpx.Response(200, json={"data": POSTS})
        return httpx.Response(503)  # RDAP down: answered once, never retried

    config = {"nb.url": "http://nb.test:3076"}
    monkeypatch.setattr(secrets, "get", lambda dotpath, default=None: config.get(dotpath, default))
    monkeypatch.setattr(toolbase, "today", lambda: date(2026, 10, 21))
    monkeypatch.setattr(
        doctor, "Client", functools.partial(Client, transport=httpx.MockTransport(handler))
    )
    ctx = doctor.Ctx()
    assert ctx.nb_heartbeat() == HEARTBEAT
    assert ctx.arcticshift_posts() == POSTS
    assert ctx.rdap_status("meikit.ai") == "unknown"
    heartbeat, search, lookup = seen
    assert str(heartbeat.url) == "http://nb.test:3076/heartbeat"
    assert "X-API-Key" not in heartbeat.headers
    assert (search.url.host, search.url.path) == (
        "arctic-shift.photon-reddit.com",
        "/api/posts/search",
    )
    assert dict(search.url.params) == {
        "query": "ad account",
        "subreddit": "FacebookAds",
        "after": "2026-09-21",
        "limit": "10",
        "sort": "desc",
    }
    assert (lookup.url.host, lookup.url.path) == ("rdap.org", "/domain/meikit.ai")


def test_the_ctx_runs_a_command_and_says_when_it_cannot(monkeypatch):
    ctx = doctor.Ctx()
    assert ctx.command([sys.executable, "-c", "print('hi')"]) == Proc(0, "hi\n", "")
    assert ctx.command(["no-such-cli-for-the-doctor"]) == Proc(
        None, "", "no-such-cli-for-the-doctor is not installed"
    )

    def too_slow(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 30)

    monkeypatch.setattr(subprocess, "run", too_slow)
    assert ctx.command(["gh", "auth", "status"]) == Proc(
        None, "", "`gh auth status` timed out after 30 s"
    )


def test_the_ctx_runs_a_selftest_in_process_and_keeps_its_output(monkeypatch):
    def add_parser(sub):
        parser = sub.add_parser("hello")
        parser.add_argument("--selftest", action="store_true")
        parser.add_argument("--fail", action="store_true")

    def run(args):
        if args.fail:
            print("hello: boom", file=sys.stderr)
            return 1
        print("OK hello 3 items")
        return 0

    monkeypatch.setitem(
        sys.modules, "factory.tools.hello", types.SimpleNamespace(add_parser=add_parser, run=run)
    )
    monkeypatch.setattr(cli, "TOOL_MODULES", ["hello"])
    ctx = doctor.Ctx()
    assert ctx.selftest(["hello", "--selftest"]) == Proc(0, "OK hello 3 items\n", "")
    assert ctx.selftest(["hello", "--selftest", "--fail"]) == Proc(1, "", "hello: boom\n")


def test_a_selftest_that_crashes_is_reported_not_raised(monkeypatch):
    def broken(argv):
        raise KeyError("x")

    monkeypatch.setattr(cli, "main", broken)
    assert doctor.Ctx().selftest(["serp_ads", "--selftest"]) == Proc(
        None, "", "crashed: KeyError (run `factory serp_ads --selftest` to see it)"
    )


def test_a_real_offline_run_touches_no_network_and_runs_nothing(monkeypatch, capsys):
    def refuse(*args, **kwargs):
        raise AssertionError(f"the offline doctor reached out: {args!r}")

    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    # The factory root of the test has no master key: the secrets fail without running bin/secrets.
    assert main(["doctor", "--offline"]) == 1
    lines = capsys.readouterr().out.splitlines()
    levels = {line.split()[0]: line.split()[1] for line in lines[2 : 2 + len(doctor.CHECKS)]}
    assert levels["secrets.master_key"] == "fail" and levels["secrets.providers"] == "fail"
    assert levels["vercel.scope"] == "skip" and levels["assets.meta"] == "warn"
    assert lines[-2] == f"eligible channels: {', '.join(HUMAN)}"


def test_a_real_offline_run_with_secrets_reads_only_them(monkeypatch, capsys):
    config = {"providers": {"searchapi": {"api_key": "k1"}, "seranking": {"api_token": "k2"}}}
    monkeypatch.setattr(secrets, "load", lambda *a, **k: config)
    monkeypatch.setattr(httpx.Client, "send", lambda *a, **k: pytest.fail("a network call"))
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("a command ran"))
    assert main(["doctor", "--offline", "--json"]) == 1  # no Firecrawl key
    checks = {c["name"]: c for c in json.loads(capsys.readouterr().out)["checks"]}
    assert checks["secrets.master_key"]["level"] == "ok"
    assert checks["secrets.providers"]["detail"] == (
        "not set: providers.firecrawl.api_key (uv run factory secrets-import-nb)"
    )
    assert "k1" not in json.dumps(checks) and "k2" not in json.dumps(checks)
