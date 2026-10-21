"""`factory doctor`: which secrets, accounts and assets exist, what they unlock, what to fix.

    factory doctor [--json] [--offline | --live]

The doctor runs CHECKS in order. A check is `Check(name, fn, needs_network, blocks)`: `fn(ctx)`
returns a `Result(ok, level, detail)`, level `ok`, `warn` or `fail`, and `blocks` names what the
check holds up when it does not pass (a channel, a recipe, a tool, the launch). A detail is one
line and reports presence only: it never quotes a secret value, nor the Vercel token. A check
reads the machine only through its `Ctx` (the secrets, the CLIs, the providers), so a test hands
it a fake one. docs/doctor.md has the table of checks and what unlocks each channel.

It prints a table `check | level | detail`, then `eligible channels: ...` and `eligible recipes:
...`: the four human channels always, a paid channel once its asset exists, every recipe but
`pre-order` until Stripe does (design D11). It exits 1 when a check fails, 0 otherwise, warnings
included.

--offline makes no network call at all, neither an API nor a CLI that calls one: it reads the
secrets, and shows each check that needs the network as `skip`. `/factory` runs it at every start,
`make check` after the tests. --live adds each provider's selftest, run in-process through
`cli.main` (`factory serp_ads --selftest`, ...): real calls that cost a few cents (SearchAPI,
SE Ranking, Firecrawl, and NeuralBox's one-turn prompt) and log nothing. --json prints
`{"checks": [{"name", "level", "ok", "detail", "blocks"}], "eligible_channels",
"eligible_recipes"}` instead.

The network checks use their own clients, one attempt each with a 20 s timeout, so a provider
that is down costs the doctor 20 s, not the minutes a research tool's retries would. SearchAPI is
asked for its account (GET /me, free), which says how many of the month's searches are left.
"""

import argparse
import contextlib
import io
import json
import re
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from factory import cli, secrets, tables, toolbase, vercel
from factory.http import Client, ProviderError
from factory.providers import arcticshift, neuralbox, rdap, searchapi

COMMAND = "doctor"
OK, WARN, FAIL, SKIP = "ok", "warn", "fail", "skip"
COLUMNS = ["check", "level", "detail"]
PROBE_TIMEOUT_S = 20.0  # a network check's one attempt
COMMAND_TIMEOUT_S = 30.0  # vercel whoami, gh auth status, dig

PROVIDER_KEYS = (
    "providers.searchapi.api_key",
    "providers.seranking.api_token",
    "providers.firecrawl.api_key",
)
SEARCHAPI_ACCOUNT = "/me"
# The words of SearchAPI's used-up quota 429 (searchapi.quota_used_up reads the same).
QUOTA_TEXT = "used all of the searches"
QUOTA_USED_UP = "SearchAPI monthly quota used up{resets}; serp_ads and ad_library are blocked"

ARCTIC_QUERY = "ad account"  # the reddit_mentions selftest's search
ARCTIC_SUBREDDIT = "FacebookAds"
ARCTIC_DAYS = 30
ARCTIC_LIMIT = 10
ARCTIC_WAIT_S = 3.0  # the wait after a throttle that names none
ARCTIC_MAX_WAIT_S = 60.0

HOBBY_WARNING = "Hobby forbids commercial use; upgrade to Pro before the first paid traffic"
LAB_DOMAIN = "meikit.ai"
VERCEL_IP = "76.76.21.21"  # Vercel's A record
VERCEL_DNS = "vercel-dns"  # in Vercel's CNAME target, cname.vercel-dns.com
LAB_DOMAIN_FREE = "lab domain not bought: /factory-setup step 1"
LAB_DOMAIN_ELSEWHERE = (
    "registered (by whom unknown; confirm with the owner or pick another lab domain)"
)
SKIPPED_DETAIL = "skipped: needs the network (run without --offline)"

HUMAN_CHANNELS = ["reddit_reply", "reddit_post", "linkedin_outreach", "community_post"]
# (asset check, the paid channel it unlocks)
ASSET_CHANNELS = [
    ("assets.google_ads", "google_search"),
    ("assets.meta", "meta_feed"),
    ("assets.sending_domain", "cold_email_b2b"),
]
RECIPES = [
    "fake-door-saas",
    "pre-order",
    "concierge-b2b",
    "cold-email-b2b",
    "complaint-response",
    "waitlist-b2c",
]
STRIPE_RECIPE = "pre-order"  # the one recipe that takes payments
# (asset check, the dotpath whose presence proves the asset, what it unlocks)
ASSETS = [
    ("assets.meta", "accounts.meta.ad_account_id", "meta_feed"),
    ("assets.google_ads", "accounts.google_ads.customer_id", "google_search"),
    ("assets.stripe", "accounts.stripe.secret_key", STRIPE_RECIPE),
    ("assets.sending_domain", "accounts.sending_domain.domain", "cold_email_b2b"),
    ("assets.resend", "accounts.resend.account_key", "the stand's email sending"),
    ("assets.turnstile", "accounts.turnstile.site_key", "the stand's anti-bot check"),
]
# (provider, the command whose selftest proves it, the level when it fails, what it holds up)
SELFTESTS = [
    ("searchapi", ["serp_ads", "--selftest"], FAIL, "serp_ads, ad_library"),
    ("seranking", ["keyword_volume", "--selftest"], FAIL, "keyword_volume"),
    ("firecrawl", ["pricing_scan", "--selftest"], FAIL, "pricing_scan"),
    ("neuralbox", ["nb", "adsinsights", "--selftest"], WARN, "nb adsinsights"),
    ("arcticshift", ["reddit_mentions", "--selftest"], WARN, "reddit_mentions"),
    ("algolia", ["hn_mentions", "--selftest"], WARN, "hn_mentions"),
    ("rdap", ["domain_check", "--selftest"], WARN, "domain_check"),
]
_GH_ACCOUNT = re.compile(r"Logged in to (\S+) (?:account|as) (\S+)")


@dataclass(frozen=True)
class Result:
    """What a check found. `level` is ok, warn or fail (skip in the output of a check --offline
    left out); `ok` says the check passed; `detail` is one line without any secret value."""

    ok: bool
    level: str
    detail: str


@dataclass(frozen=True)
class Proc:
    """What a command did: its exit code, None when it could not run or timed out (`err` then
    says why), and what it printed."""

    code: int | None
    out: str
    err: str


def passed(detail: str) -> Result:
    return Result(True, OK, detail)


def warning(detail: str) -> Result:
    return Result(False, WARN, detail)


def failure(detail: str) -> Result:
    return Result(False, FAIL, detail)


SKIPPED = Result(False, SKIP, SKIPPED_DETAIL)


class Ctx:
    """The machine as the checks see it: the secrets, the CLIs, the providers.

    `offline` says the run makes no network call: `run_checks` skips the checks that need the
    network, and secrets.providers keeps to the keys' presence. The Vercel account is read once,
    by `vercel_user`, and kept for the checks after it.
    """

    def __init__(self, offline: bool = False) -> None:
        self.offline = offline
        self._vercel_user: dict | vercel.VercelError | None = None

    def load_secrets(self) -> None:
        """Decrypt the factory config; SecretsUnavailable says why it cannot be."""
        secrets.load()

    def has_secret(self, dotpath: str) -> bool:
        """Whether the factory config has a value at `dotpath`, never the value itself;
        SecretsUnavailable when the config cannot be read."""
        return secrets.get(dotpath, None) is not None

    def command(self, argv: list[str], timeout_s: float = COMMAND_TIMEOUT_S) -> Proc:
        """Run `argv` with no input and keep what it printed."""
        try:
            proc = subprocess.run(
                argv,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                stdin=subprocess.DEVNULL,
                timeout=timeout_s,
                check=False,
            )
        except FileNotFoundError:
            return Proc(None, "", f"{argv[0]} is not installed")
        except subprocess.TimeoutExpired:
            return Proc(None, "", f"`{' '.join(argv)}` timed out after {timeout_s:g} s")
        except OSError as exc:
            return Proc(None, "", f"cannot run {argv[0]}: {exc.strerror or exc}")
        return Proc(proc.returncode, proc.stdout, proc.stderr)

    def searchapi_account(self) -> dict:
        """SearchAPI's account, GET /me (free): `account.remaining_credits` and
        `subscription.period_end`. ProviderError when it does not answer, at once for the
        used-up quota's 429."""
        params = {"api_key": secrets.get("providers.searchapi.api_key")}
        with self._client(
            "searchapi", searchapi.BASE_URL, params=params, fatal=searchapi.quota_used_up
        ) as client:
            return client.get_json(SEARCHAPI_ACCOUNT)

    def nb_heartbeat(self) -> dict:
        """NeuralBox's heartbeat at `nb.url` (its local address without one): no key needed."""
        with self._client("neuralbox", self._nb_url()) as client:
            return neuralbox.heartbeat(client)

    def arcticshift_posts(self) -> list[dict]:
        """One Arctic Shift search, the reddit_mentions selftest's: the newest posts of the last
        30 days. SlowDown for Arctic Shift's 422, ProviderError for any other failure."""
        after = (toolbase.today() - timedelta(days=ARCTIC_DAYS)).isoformat()
        with self._client("arcticshift", arcticshift.BASE_URL) as client:
            return arcticshift.posts_search(
                client, ARCTIC_QUERY, subreddit=ARCTIC_SUBREDDIT, after=after, limit=ARCTIC_LIMIT
            )

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def rdap_status(self, domain: str) -> str:
        """`taken`, `available` or `unknown` by RDAP (rdap.status)."""
        with self._client("rdap", rdap.BASE_URL) as client:
            return rdap.status(client, domain)

    def vercel_scope(self) -> tuple[str, str | None]:
        """The CLI's scope from its config.json (vercel.current_scope): no token, no call."""
        return vercel.current_scope()

    def vercel_user(self) -> dict:
        """The Vercel account (vercel.user_plan), read once and kept, a VercelError too."""
        if self._vercel_user is None:
            try:
                self._vercel_user = vercel.user_plan()
            except vercel.VercelError as exc:
                self._vercel_user = exc
        if isinstance(self._vercel_user, vercel.VercelError):
            raise self._vercel_user
        return self._vercel_user

    def selftest(self, argv: list[str]) -> Proc:
        """Run `factory <argv>` in-process through cli.main and keep what it printed. A tool
        that crashes is reported by its exception's type, not raised."""
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = cli.main(argv)
        except Exception as exc:  # a bug in the tool: one row, the other checks still run
            command = " ".join(argv)
            return Proc(
                None, "", f"crashed: {type(exc).__name__} (run `factory {command}` to see it)"
            )
        return Proc(code, out.getvalue(), err.getvalue())

    def _client(self, provider: str, base_url: str, **options: object) -> Client:
        return Client(provider, base_url, timeout_s=PROBE_TIMEOUT_S, retries=1, **options)

    def _nb_url(self) -> str:
        try:
            return secrets.get("nb.url", neuralbox.LOCAL_URL)
        except secrets.SecretsError:
            return neuralbox.LOCAL_URL


@dataclass(frozen=True)
class Check:
    """One check: `fn(ctx)` is its Result; a `needs_network` check is skipped --offline;
    `blocks` is what it holds up when it does not pass."""

    name: str
    fn: Callable[[Ctx], Result]
    needs_network: bool
    blocks: str


def check_master_key(ctx: Ctx) -> Result:
    try:
        ctx.load_secrets()
    except secrets.SecretsError as exc:
        return failure(str(exc))
    return passed("secrets/master.key opens secrets/config.yml.enc")


def check_provider_keys(ctx: Ctx) -> Result:
    """The research keys are set; online, SearchAPI also has searches left this month."""
    try:
        missing = [dotpath for dotpath in PROVIDER_KEYS if not ctx.has_secret(dotpath)]
    except secrets.SecretsError:
        return failure("the secrets cannot be read (see secrets.master_key)")
    if missing:
        return failure(f"not set: {', '.join(missing)} (uv run factory secrets-import-nb)")
    present = "searchapi, seranking and firecrawl keys present"
    if ctx.offline:
        return passed(present)
    try:
        account = ctx.searchapi_account()
    except ProviderError as exc:
        if exc.status == 429 and QUOTA_TEXT in exc.detail.lower():
            return failure(QUOTA_USED_UP.format(resets=""))
        if exc.status in (401, 403):
            return failure(f"{present}, but SearchAPI refused its key: {exc}")
        return warning(f"{present}; SearchAPI did not answer: {exc}")
    quota = account.get("account") if isinstance(account, dict) else None
    remaining = quota.get("remaining_credits") if isinstance(quota, dict) else None
    if not _is_number(remaining):
        return warning(f"{present}; SearchAPI's account gives no remaining_credits")
    if remaining <= 0:
        return failure(QUOTA_USED_UP.format(resets=_resets(account)))
    allowance = quota.get("monthly_allowance")
    of = f" of {allowance}" if _is_number(allowance) else ""
    return passed(f"{present}; SearchAPI: {remaining}{of} searches left this month")


def check_nb_heartbeat(ctx: Ctx) -> Result:
    try:
        beat = ctx.nb_heartbeat()
    except ProviderError as exc:
        return warning(f"NeuralBox unreachable: {exc}")
    listed = beat.get("available_tools")
    tools = [tool for tool in listed if isinstance(tool, str)] if isinstance(listed, list) else []
    missing = [tool for tool in neuralbox.WHITELIST if tool not in tools]
    if missing:
        return warning(
            f"NeuralBox up: {_plural(len(tools), 'tool')}, but not {', '.join(missing)}: "
            "nb adsinsights is blocked"
        )
    return passed(f"NeuralBox up: {_plural(len(tools), 'tool')}, the AdsInsights ones included")


def check_arcticshift(ctx: Ctx) -> Result:
    """One 30-day search; a throttle is waited out once (60 s at most). Never a failure: Arctic
    Shift is free, and reddit_mentions waits out what it can."""
    waited: float | None = None
    try:
        try:
            posts = ctx.arcticshift_posts()
        except arcticshift.SlowDown as exc:
            waited = min(ARCTIC_WAIT_S if exc.reset_s is None else exc.reset_s, ARCTIC_MAX_WAIT_S)
            ctx.sleep(waited)
            posts = ctx.arcticshift_posts()
    except arcticshift.SlowDown:
        return warning(
            f"throttled: Arctic Shift refused again after a {waited:g} s wait; "
            "reddit_mentions waits it out"
        )
    except ProviderError as exc:
        return warning(f"Arctic Shift did not answer: {exc}")
    after = "" if waited is None else f", after a {waited:g} s throttle"
    return passed(f"30-day posts search: {_plural(len(posts), 'post')}{after}")


def check_vercel_login(ctx: Ctx) -> Result:
    proc = ctx.command(["vercel", "whoami"])
    if proc.code is None:
        return failure(proc.err)
    if proc.code != 0:
        why = _last_line(proc.err) or _last_line(proc.out) or f"exit {proc.code}"
        return failure(f"`vercel whoami` failed: {why}; run `vercel login`")
    name = _last_line(proc.out)
    return passed(f"logged in as {name}" if name else "logged in")


def check_vercel_scope(ctx: Ctx) -> Result:
    """The CLI works in the personal scope: no current team, on an account that has one (a
    team-based, northstar, account has none: its CLI always works in a team)."""
    kind, team = ctx.vercel_scope()
    try:
        user = ctx.vercel_user()
    except vercel.VercelError as exc:
        if kind == "team":
            return failure(
                f"CLI scope is team {team}, not personal: run `vercel switch <username>` ({exc})"
            )
        return failure(f"the Vercel account cannot be read, so its scope is unconfirmed: {exc}")
    name = user["username"]
    if user["northstar"]:
        where = (
            f"CLI scope is team {team}"
            if kind == "team"
            else "the CLI works in the account's default team"
        )
        return failure(
            f"{where}: {name} is a team-based (northstar) account, which has no personal scope "
            f"and refuses `vercel switch {name}`; see docs/doctor.md"
        )
    if kind == "team":
        return failure(f"CLI scope is team {team}, not personal: run `vercel switch {name}`")
    return passed(f"personal scope ({name})")


def check_vercel_plan(ctx: Ctx) -> Result:
    try:
        plan = ctx.vercel_user()["plan"]
    except vercel.VercelError as exc:
        return warning(f"the plan cannot be read: {exc}")
    if plan == "hobby":
        return warning(HOBBY_WARNING)
    if not plan:
        return warning("GET /v2/user gives no plan")
    return passed(f"{plan} plan")


def check_gh_auth(ctx: Ctx) -> Result:
    """`gh auth status` passes, so `gh` can create the idea repos. Its output is read for the
    account name only, never shown."""
    proc = ctx.command(["gh", "auth", "status"])
    if proc.code is None:
        return failure(proc.err)
    if proc.code != 0:
        return failure(f"`gh auth status` failed (exit {proc.code}): run `gh auth login`")
    match = _GH_ACCOUNT.search(f"{proc.out}\n{proc.err}")
    return passed(f"logged in to {match[1]} as {match[2]}" if match else "logged in")


def check_lab_domain(ctx: Ctx) -> Result:
    """The lab domain is registered and its DNS points at Vercel (an A record 76.76.21.21 or a
    vercel-dns CNAME)."""
    try:
        status = ctx.rdap_status(LAB_DOMAIN)
    except ProviderError as exc:
        return warning(f"RDAP lookup failed: {exc}")
    if status == "available":
        return warning(LAB_DOMAIN_FREE)
    if status != "taken":
        return warning(f"RDAP cannot tell whether {LAB_DOMAIN} is registered")
    proc = ctx.command(["dig", "+short", LAB_DOMAIN])
    if proc.code is None:
        return warning(f"registered; {proc.err}")
    if proc.code != 0:
        return warning(f"registered; `dig +short {LAB_DOMAIN}` failed (exit {proc.code})")
    answers = proc.out.split()
    if VERCEL_IP in answers or any(VERCEL_DNS in answer for answer in answers):
        return passed(f"{LAB_DOMAIN} registered and pointed at Vercel")
    return warning(LAB_DOMAIN_ELSEWHERE)


def asset_check(dotpath: str, unlocks: str) -> Callable[[Ctx], Result]:
    """The check of one asset: `dotpath` is set in the factory config (its value never read
    out). A warning when it is not, naming what stays locked."""

    def check(ctx: Ctx) -> Result:
        try:
            present = ctx.has_secret(dotpath)
        except secrets.SecretsError:
            return warning(f"the secrets cannot be read: {unlocks} stays locked")
        if present:
            return passed(f"{dotpath} set: unlocks {unlocks}")
        return warning(f"{dotpath} not set: {unlocks} stays locked (/factory-setup)")

    return check


def selftest_check(argv: list[str], level: str) -> Callable[[Ctx], Result]:
    """The check that runs `factory <argv>` (a selftest): its `OK ...` line, or what it printed
    last at `level`."""

    def check(ctx: Ctx) -> Result:
        proc = ctx.selftest(argv)
        if proc.code == 0:
            return passed(_last_line(proc.out) or "OK")
        why = _last_line(proc.err) or _last_line(proc.out) or f"exit {proc.code}"
        return Result(False, level, why)

    return check


CHECKS: list[Check] = [
    Check("secrets.master_key", check_master_key, False, "every tool that reads a key"),
    Check(
        "secrets.providers",
        check_provider_keys,
        False,
        "serp_ads, ad_library, keyword_volume, pricing_scan",
    ),
    Check("nb.heartbeat", check_nb_heartbeat, True, "nb adsinsights"),
    Check("provider.arcticshift", check_arcticshift, True, "reddit_mentions"),
    Check("vercel.login", check_vercel_login, True, "launch"),
    Check("vercel.scope", check_vercel_scope, True, "launch"),
    Check("vercel.plan", check_vercel_plan, True, "paid traffic"),
    Check("gh.auth", check_gh_auth, True, "launch"),
    Check("domain.meikit", check_lab_domain, True, f"launch on <slug>.{LAB_DOMAIN}"),
    *[
        Check(name, asset_check(dotpath, unlocks), False, unlocks)
        for name, dotpath, unlocks in ASSETS
    ],
]
# --live only: each provider's selftest, after CHECKS.
LIVE_CHECKS: list[Check] = [
    Check(f"selftest.{provider}", selftest_check(argv, level), True, blocks)
    for provider, argv, level, blocks in SELFTESTS
]


def run_checks(checks: list[Check], ctx: Ctx) -> dict[str, Result]:
    """Each check's Result by name, in order; a check that needs the network is SKIPPED when
    `ctx.offline`."""
    return {
        check.name: SKIPPED if ctx.offline and check.needs_network else check.fn(ctx)
        for check in checks
    }


def eligible_channels(results: dict[str, Result]) -> list[str]:
    """The channels an experiment may use: the human ones always, a paid one once its asset
    check passed."""
    return [
        *HUMAN_CHANNELS,
        *(channel for name, channel in ASSET_CHANNELS if _passed(results, name)),
    ]


def eligible_recipes(results: dict[str, Result]) -> list[str]:
    """Every recipe, but `pre-order` only once the Stripe check passed."""
    return [
        recipe for recipe in RECIPES if recipe != STRIPE_RECIPE or _passed(results, "assets.stripe")
    ]


def add_parser(sub: argparse._SubParsersAction) -> None:
    parser = sub.add_parser(
        COMMAND,
        help="which secrets, accounts and assets exist, and the channels and recipes they unlock",
        description="Check the secrets, the provider keys and quotas, NeuralBox, Vercel, gh, the "
        "lab domain and the ad and payment assets; print what each blocks and the eligible "
        "channels and recipes. Exit 1 when a check fails.",
    )
    parser.add_argument(
        "--json", action="store_true", help="print the checks and the eligible sets as JSON"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--offline",
        action="store_true",
        help="make no network call: read the secrets, skip the checks that need the network",
    )
    mode.add_argument(
        "--live",
        action="store_true",
        help="also run each provider's selftest (real calls, a few cents, nothing logged)",
    )


def run(args: argparse.Namespace) -> int:
    ctx = Ctx(offline=args.offline)
    checks = [*CHECKS, *(LIVE_CHECKS if args.live else [])]
    results = run_checks(checks, ctx)
    if args.json:
        print(json.dumps(report(checks, results), indent=2, ensure_ascii=False))
    else:
        print(summary(checks, results))
    return 1 if any(result.level == FAIL for result in results.values()) else 0


def report(checks: list[Check], results: dict[str, Result]) -> dict:
    """The --json output."""
    return {
        "checks": [
            {
                "name": check.name,
                "level": results[check.name].level,
                "ok": results[check.name].ok,
                "detail": results[check.name].detail,
                "blocks": check.blocks,
            }
            for check in checks
        ],
        "eligible_channels": eligible_channels(results),
        "eligible_recipes": eligible_recipes(results),
    }


def summary(checks: list[Check], results: dict[str, Result]) -> str:
    """The table `check | level | detail`, then the eligible channels and recipes."""
    rows = [
        {
            "check": check.name,
            "level": results[check.name].level,
            "detail": results[check.name].detail,
        }
        for check in checks
    ]
    return "\n".join(
        [
            tables.render(rows, COLUMNS),
            f"eligible channels: {', '.join(eligible_channels(results))}",
            f"eligible recipes: {', '.join(eligible_recipes(results))}",
        ]
    )


def _passed(results: dict[str, Result], name: str) -> bool:
    result = results.get(name)
    return result is not None and result.ok


def _resets(account: dict) -> str:
    """` (resets YYYY-MM-DD)`, the end of SearchAPI's billing period; empty when it gives none."""
    subscription = account.get("subscription")
    end = subscription.get("period_end") if isinstance(subscription, dict) else None
    try:
        day = datetime.fromisoformat(end).date()
    except TypeError, ValueError:
        return ""
    return f" (resets {day.isoformat()})"


def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def _last_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else ""
