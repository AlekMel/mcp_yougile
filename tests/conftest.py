"""Shared pytest fixtures for the YouGile MCP test suite."""

from __future__ import annotations

import os

import pytest

# Ensure config never blocks imports/tests by providing a dummy key/base.
os.environ.setdefault("YOUGILE_API_KEY", "test-key")
os.environ.setdefault("YOUGILE_BASE_URL", "https://api.test")


@pytest.fixture(autouse=True)
async def _reset_client():
    """Reset the cached httpx client around each test so respx mounts cleanly."""
    from yougile_mcp import client

    await client.aclose()
    yield
    await client.aclose()
