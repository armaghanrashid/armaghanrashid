"""Latest workflow-run status per project repo, straight from the GitHub API.

A status is never guessed: anything that is not a clear success or failure
(network error, 404, no runs, still running, cancelled) is reported as unknown.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import requests

OK, FAIL, UNKNOWN = "ok", "fail", "unknown"
API = "https://api.github.com"
FAILED_CONCLUSIONS = {"failure", "timed_out", "startup_failure"}


def _headers(token: str | None) -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def map_conclusion(conclusion: str | None) -> str:
    if conclusion == "success":
        return OK
    if conclusion in FAILED_CONCLUSIONS:
        return FAIL
    return UNKNOWN


def _get_json(get: Callable[..., Any], url: str, token: str | None, params=None) -> Any:
    response = get(url, headers=_headers(token), params=params, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"{url} -> HTTP {response.status_code}")
    return response.json()


def fetch_status(
    login: str, repo: str, token: str | None = None, get: Callable[..., Any] = requests.get
) -> str:
    """Status of the latest workflow run on the repo's default branch."""
    try:
        info = _get_json(get, f"{API}/repos/{login}/{repo}", token)
        branch = info["default_branch"]
        runs = _get_json(
            get,
            f"{API}/repos/{login}/{repo}/actions/runs",
            token,
            params={"per_page": 1, "branch": branch},
        )
        items = runs["workflow_runs"]
        if not items:
            return UNKNOWN
        return map_conclusion(items[0].get("conclusion"))
    except (requests.RequestException, RuntimeError, ValueError, KeyError, TypeError):
        return UNKNOWN


def fetch_all(
    login: str, repos: list[str], token: str | None = None, get: Callable[..., Any] = requests.get
) -> dict[str, str]:
    return {repo: fetch_status(login, repo, token, get) for repo in repos}
