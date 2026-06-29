"""Tests for the shared HTTP layer (client.py)."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from yougile_mcp import client

BASE = "https://api.test"


@respx.mock
async def test_get_sends_auth_header_and_returns_json():
    route = respx.get(f"{BASE}/api-v2/users/me").mock(
        return_value=httpx.Response(200, json={"id": "u1", "name": "Иван"})
    )
    result = await client.call_api("GET", "/api-v2/users/me")

    assert route.called
    assert route.calls.last.request.headers["Authorization"] == "Bearer test-key"
    assert json.loads(result) == {"id": "u1", "name": "Иван"}


@respx.mock
async def test_none_params_and_body_are_dropped():
    route = respx.post(f"{BASE}/api-v2/tasks").mock(
        return_value=httpx.Response(200, json={"id": "t1"})
    )
    await client.call_api(
        "POST",
        "/api-v2/tasks",
        params={"a": 1, "b": None},
        json_body={"title": "x", "desc": None},
    )

    request = route.calls.last.request
    assert "b" not in str(request.url)
    assert json.loads(request.content) == {"title": "x"}


@respx.mock
async def test_401_returns_actionable_message():
    respx.get(f"{BASE}/api-v2/users/me").mock(return_value=httpx.Response(401, text="no"))
    result = await client.call_api("GET", "/api-v2/users/me")
    assert "Authentication failed" in result
    assert "YOUGILE_API_KEY" in result


@respx.mock
async def test_404_returns_not_found_message():
    respx.get(f"{BASE}/api-v2/tasks/zzz").mock(return_value=httpx.Response(404, text="missing"))
    result = await client.call_api("GET", "/api-v2/tasks/zzz")
    assert "not found (404)" in result


@respx.mock
async def test_empty_response_body_is_ok():
    respx.delete(f"{BASE}/api-v2/users/u1").mock(return_value=httpx.Response(200))
    result = await client.call_api("DELETE", "/api-v2/users/u1")
    assert json.loads(result) == {}
