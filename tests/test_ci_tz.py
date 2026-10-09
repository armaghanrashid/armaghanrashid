from __future__ import annotations

from datetime import UTC, datetime

import pytest
import requests

from profile_gen import ci
from profile_gen.tz import utc_offset_label


class Resp:
    def __init__(self, payload, status=200):
        self.payload, self.status_code = payload, status

    def json(self):
        return self.payload


def fake_get(conclusion="success", branch="main", runs=True, calls=None):
    def get(url, headers=None, params=None, timeout=None):
        if calls is not None:
            calls.append((url, headers, params))
        if url.endswith("/actions/runs"):
            items = [{"conclusion": conclusion, "head_branch": params["branch"]}] if runs else []
            return Resp({"workflow_runs": items})
        return Resp({"default_branch": branch})

    return get


@pytest.mark.parametrize(
    ("conclusion", "expected"),
    [
        ("success", ci.OK), ("failure", ci.FAIL), ("timed_out", ci.FAIL),
        ("startup_failure", ci.FAIL), ("cancelled", ci.UNKNOWN), ("skipped", ci.UNKNOWN),
        (None, ci.UNKNOWN), ("neutral", ci.UNKNOWN),
    ],
)
def test_conclusion_mapping(conclusion, expected):
    assert ci.fetch_status("me", "r", get=fake_get(conclusion)) == expected


def test_no_runs_is_unknown():
    assert ci.fetch_status("me", "r", get=fake_get(runs=False)) == ci.UNKNOWN


def test_queries_default_branch_with_per_page_one():
    calls = []
    ci.fetch_status("me", "r", get=fake_get(branch="trunk", calls=calls))
    url, _, params = calls[1]
    assert url == "https://api.github.com/repos/me/r/actions/runs"
    assert params == {"per_page": 1, "branch": "trunk"}


def test_token_is_sent_only_when_present():
    calls = []
    ci.fetch_status("me", "r", token="tkn", get=fake_get(calls=calls))
    assert all(h["Authorization"] == "Bearer tkn" for _, h, _ in calls)
    calls.clear()
    ci.fetch_status("me", "r", get=fake_get(calls=calls))
    assert all("Authorization" not in h for _, h, _ in calls)


def test_api_failures_are_unknown_never_invented():
    def boom(*a, **k):
        raise requests.ConnectionError("offline")

    def not_found(*a, **k):
        return Resp({"message": "Not Found"}, 404)

    def garbage(*a, **k):
        return Resp({"unexpected": True})

    for get in (boom, not_found, garbage):
        assert ci.fetch_status("me", "r", get=get) == ci.UNKNOWN


def test_fetch_all_maps_each_repo():
    assert ci.fetch_all("me", ["a", "b"], get=fake_get("failure")) == {"a": ci.FAIL, "b": ci.FAIL}


def test_offset_in_summer_is_minus_four():
    assert utc_offset_label(datetime(2026, 7, 1, 12, tzinfo=UTC), "America/Montreal") == "UTC−4"


def test_offset_in_winter_is_minus_five():
    assert utc_offset_label(datetime(2026, 1, 15, 12, tzinfo=UTC), "America/Montreal") == "UTC−5"


def test_offset_uses_real_minus_and_handles_positive_and_half_hours():
    assert "−" in utc_offset_label(datetime(2026, 1, 1, tzinfo=UTC), "America/Montreal")
    assert utc_offset_label(datetime(2026, 1, 1, tzinfo=UTC), "Asia/Kolkata") == "UTC+5:30"
    assert utc_offset_label(datetime(2026, 1, 1, tzinfo=UTC), "UTC") == "UTC+0"
