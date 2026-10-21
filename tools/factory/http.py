"""The one HTTP client every research provider goes through.

A `Client` wraps an `httpx.Client` for one provider (its base URL, plus the headers or query
parameters that carry its credentials) and adds what every research API here needs:

- pacing: consecutive requests start at least `pace_s` seconds apart (SE Ranking 2.5 s);
- retries: a 429, a 5xx, a network error, or a response `retry_on` accepts is tried again, up to
  `retries` attempts in all, sleeping `max(2 * n, hint)` seconds before attempt n, where the hint
  is the provider's Retry-After or X-RateLimit-Reset, capped at 300 s; a response `fatal` accepts
  (SearchAPI's "used all of the searches for the month" 429) raises at once, without a retry;
- dry runs: with `dry_run=True` every call is answered from `fixtures/<fixture>.json` and nothing
  touches the network; `calls` still counts the calls, so a tool can preview its cost;
- errors: `ProviderError` names the provider and the status and never quotes a secret.

`get` and `post` return the final response whatever its status (RDAP reads a 404 as an answer);
`get_json` and `post_json` decode a 2xx body and raise ProviderError for anything else. Every
sleep goes through `time.sleep`, which the tests replace.
"""

import json
import logging
import math
import re
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, Self

import httpx

from factory import secrets

FIXTURES = Path(__file__).resolve().parent / "fixtures"
"""Dry-run answers, one real response each: `<provider>/<name>.json`."""

MAX_HINT_S = 300.0  # the longest a provider's Retry-After or X-RateLimit-Reset can make us wait
EPOCH_FROM = 100_000  # an X-RateLimit-Reset this large is a Unix time, not a number of seconds
DETAIL_MAX = 300

# The value of a query parameter that carries a credential: `api_key=`, `apikey=`, `token=`, `key=`.
_CREDENTIAL_PARAM = re.compile(r"(?i)(?<!\w)(api_key|apikey|token|key)=[^&\s\"'<>#)\]},;:]+")

# httpx logs every request URL at INFO, and SearchAPI's key rides in its URLs: keep that log off.
logging.getLogger("httpx").setLevel(logging.WARNING)


class ProviderError(Exception):
    """A provider call failed: a non-2xx final status, or a network error (`status` None).

    `detail` never quotes a secret: it goes through `secrets.redact` when the secrets load, then
    loses the value of every `api_key`, `apikey`, `token` or `key` query parameter, then is joined
    into one line and cut to 300 characters. The message reads `<provider>: HTTP <status>: <detail>`
    or `<provider>: network error: <detail>`.
    """

    def __init__(self, provider: str, status: int | None, detail: str) -> None:
        self.provider = provider
        self.status = status
        self.detail = _scrub(detail)
        what = "network error" if status is None else f"HTTP {status}"
        super().__init__(f"{provider}: {what}: {self.detail}")


class Client:
    """One provider's HTTP client: pacing, retries, dry-run fixtures and secret-free errors.

    `headers` and `params` go with every request (a provider's credentials travel there).
    `retry_on` makes more responses worth a retry than 429 and 5xx (Arctic Shift's 422 "slow
    down"); `fatal` picks responses no retry can help (a used-up monthly quota): even `get` and
    `post` raise ProviderError on those, at once. `calls` counts the get/post calls made, dry-run
    ones included, a retried call once.
    """

    def __init__(
        self,
        provider: str,
        base_url: str,
        headers: dict | None = None,
        pace_s: float = 0.0,
        retries: int = 3,
        timeout_s: float = 90.0,
        dry_run: bool = False,
        transport: httpx.BaseTransport | None = None,
        *,
        params: dict | None = None,
        retry_on: Callable[[httpx.Response], bool] | None = None,
        fatal: Callable[[httpx.Response], bool] | None = None,
    ) -> None:
        self.provider = provider
        self.base_url = base_url
        self.pace_s = pace_s
        self.retries = max(1, retries)
        self.dry_run = dry_run
        self.retry_on = retry_on
        self.fatal = fatal
        self.calls = 0
        self._last_start: float | None = None
        # A dry run never gets a connection pool, so it cannot reach the network.
        self._http = None
        if not dry_run:
            self._http = httpx.Client(
                base_url=base_url,
                headers=headers,
                params=params,
                timeout=timeout_s,
                follow_redirects=True,
                transport=transport,
            )

    def get(
        self, path: str, params: dict | None = None, *, fixture: str | None = None
    ) -> httpx.Response:
        """GET `path`, leaving out the params whose value is None; the final response, any status."""
        if params:
            params = {name: value for name, value in params.items() if value is not None}
        return self._send("GET", path, fixture, params=params)

    def post(self, path: str, json: Any = None, *, fixture: str | None = None) -> httpx.Response:
        """POST `json` to `path`; the final response, any status."""
        return self._send("POST", path, fixture, json=json)

    def get_json(self, path: str, params: dict | None = None, *, fixture: str | None = None) -> Any:
        """The decoded body of a 2xx GET; ProviderError for any other final status."""
        return self._decode(self.get(path, params, fixture=fixture))

    def post_json(self, path: str, json: Any = None, *, fixture: str | None = None) -> Any:
        """The decoded body of a 2xx POST; ProviderError for any other final status."""
        return self._decode(self.post(path, json, fixture=fixture))

    def close(self) -> None:
        if self._http is not None:
            self._http.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def _send(self, method: str, path: str, fixture: str | None, **kwargs: Any) -> httpx.Response:
        self.calls += 1
        if self._http is None:
            return self._replay(method, path, fixture)
        response: httpx.Response | None = None
        error: httpx.RequestError | None = None
        for attempt in range(1, self.retries + 1):
            if attempt > 1:
                time.sleep(self._backoff(attempt, response))
            self._pace()
            try:
                response = self._http.request(method, path, **kwargs)
            except httpx.RequestError as exc:  # network errors, timeouts: a failed attempt
                response, error = None, exc
                continue
            if self.fatal is not None and self.fatal(response):
                raise self._error(response, response.text)
            if not self._worth_retrying(response):
                break
        if response is None:
            raise ProviderError(
                self.provider, None, f"{method} {path}: {type(error).__name__}: {error}"
            )
        return response

    def _replay(self, method: str, path: str, fixture: str | None) -> httpx.Response:
        """The dry-run answer: a 200 carrying `fixtures/<fixture>.json` (FileNotFoundError if none)."""
        if fixture is None:
            raise ValueError(f"{self.provider}: {method} {path} has no dry-run fixture")
        data = json.loads((FIXTURES / f"{fixture}.json").read_text(encoding="utf-8"))
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        return httpx.Response(200, json=data, request=httpx.Request(method, url))

    def _pace(self) -> None:
        """Wait until `pace_s` has passed since the previous request started (never before the
        first). The wait is rounded up to whole centiseconds, so it never falls short of pace_s."""
        if self.pace_s > 0 and self._last_start is not None:
            wait = self.pace_s - (time.monotonic() - self._last_start)
            if wait > 0:
                time.sleep(math.ceil(wait * 100) / 100)
        self._last_start = time.monotonic()

    def _worth_retrying(self, response: httpx.Response) -> bool:
        status = response.status_code
        if status == 429 or status >= 500:
            return True
        return self.retry_on is not None and self.retry_on(response)

    def _backoff(self, attempt: int, response: httpx.Response | None) -> float:
        """Seconds to sleep before `attempt` (2, 3, ...): 2 s per attempt, or the provider's hint."""
        hint = _wait_hint(response.headers) if response is not None else 0.0
        return max(2.0 * attempt, hint)

    def _decode(self, response: httpx.Response) -> Any:
        if not response.is_success:
            raise self._error(response, response.text)
        try:
            return response.json()
        except ValueError:  # not JSON, or not text at all
            raise self._error(response, f"not JSON: {response.text}") from None

    def _error(self, response: httpx.Response, text: str) -> ProviderError:
        request = response.request
        target = request.url.raw_path.decode("ascii", "replace")  # path and query string
        return ProviderError(
            self.provider, response.status_code, f"{request.method} {target}: {text}"
        )


def _wait_hint(headers: httpx.Headers) -> float:
    """The provider's own wait in seconds, capped at 300; 0 when it gives none.

    Retry-After is a number of seconds. X-RateLimit-Reset is one too, unless it is 100000 or
    more: then it is the Unix time at which the limit resets.
    """
    for name in ("Retry-After", "X-RateLimit-Reset"):
        try:
            value = float(headers[name])
        except KeyError, ValueError:
            continue
        if not math.isfinite(value):
            continue
        if name == "X-RateLimit-Reset" and value >= EPOCH_FROM:
            value -= time.time()
        return min(max(value, 0.0), MAX_HINT_S)
    return 0.0


def _scrub(text: str) -> str:
    """`text` without known secret values or credential query values, on one line, cut to 300."""
    try:
        text = secrets.redact(text)  # leaves text unchanged when the secrets cannot load
    except secrets.SecretsError:
        pass
    text = _CREDENTIAL_PARAM.sub(r"\1=***", text)
    return " ".join(text.split())[:DETAIL_MAX]
