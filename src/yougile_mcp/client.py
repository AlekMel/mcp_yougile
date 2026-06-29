"""Shared HTTP layer for the YouGile API.

All tools go through :func:`call_api`, which performs the request, formats a
successful JSON payload and converts any error into an actionable message
string. This keeps every tool implementation a thin, declarative mapping onto
an endpoint and centralises auth, pagination params and error handling.
"""

from __future__ import annotations

import json
from typing import Any, Optional

import httpx

from .config import ConfigError, REQUEST_TIMEOUT, get_api_key, get_base_url

_client: Optional[httpx.AsyncClient] = None


def _get_client() -> httpx.AsyncClient:
    """Return a cached AsyncClient configured with base URL and auth header."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=get_base_url(),
            headers={"Authorization": f"Bearer {get_api_key()}"},
            timeout=REQUEST_TIMEOUT,
        )
    return _client


async def aclose() -> None:
    """Close the cached client (used on shutdown / in tests)."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def _clean(data: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """Drop keys whose value is ``None`` so we never send empty fields."""
    if data is None:
        return None
    return {k: v for k, v in data.items() if v is not None}


async def api_request(
    method: str,
    path: str,
    *,
    params: Optional[dict[str, Any]] = None,
    json_body: Optional[dict[str, Any]] = None,
) -> Any:
    """Perform a single authenticated request and return the parsed JSON body.

    Raises ``httpx.HTTPStatusError`` on non-2xx responses.
    """
    client = _get_client()
    response = await client.request(
        method.upper(),
        path,
        params=_clean(params),
        json=_clean(json_body),
    )
    response.raise_for_status()
    if not response.content:
        return {}
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"raw": response.text}


def format_result(data: Any) -> str:
    """Serialise a successful result as pretty JSON (Cyrillic kept readable)."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def handle_error(exc: Exception) -> str:
    """Convert an exception into a clear, actionable error string for the agent."""
    if isinstance(exc, ConfigError):
        return f"Error: {exc}"
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        detail = exc.response.text.strip()
        if status == 401:
            return (
                "Error: Authentication failed (401). Check that YOUGILE_API_KEY "
                "is a valid, non-expired YouGile API key."
            )
        if status == 403:
            return f"Error: Permission denied (403). {detail}"
        if status == 404:
            return f"Error: Resource not found (404). Check the provided id. {detail}"
        if status == 429:
            return "Error: Rate limit exceeded (429). Wait before retrying."
        return f"Error: API request failed with status {status}. {detail}"
    if isinstance(exc, httpx.TimeoutException):
        return "Error: Request to YouGile timed out. Please try again."
    if isinstance(exc, httpx.RequestError):
        return f"Error: Network error contacting YouGile: {exc}"
    return f"Error: Unexpected {type(exc).__name__}: {exc}"


async def call_api(
    method: str,
    path: str,
    *,
    params: Optional[dict[str, Any]] = None,
    json_body: Optional[dict[str, Any]] = None,
) -> str:
    """Run a request and return a formatted result or a formatted error string.

    This is the single entry point used by every tool.
    """
    try:
        data = await api_request(method, path, params=params, json_body=json_body)
        return format_result(data)
    except Exception as exc:  # noqa: BLE001 - converted to an actionable message
        return handle_error(exc)


async def call_api_upload(path: str, *, filename: str, content: bytes) -> str:
    """Upload a file via multipart/form-data and return a formatted result string."""
    try:
        client = _get_client()
        response = await client.post(path, files={"file": (filename, content)})
        response.raise_for_status()
        data = response.json() if response.content else {}
        return format_result(data)
    except Exception as exc:  # noqa: BLE001 - converted to an actionable message
        return handle_error(exc)
