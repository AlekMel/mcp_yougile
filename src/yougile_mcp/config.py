"""Configuration for the YouGile MCP server.

Values are read lazily from environment variables so that importing the package
(e.g. during tests or tool discovery) never fails just because credentials are
not configured yet.
"""

from __future__ import annotations

import os

DEFAULT_BASE_URL = "https://ru.yougile.com"
API_KEY_ENV = "YOUGILE_API_KEY"
BASE_URL_ENV = "YOUGILE_BASE_URL"

# Network timeout (seconds) for all API requests.
REQUEST_TIMEOUT = 30.0


class ConfigError(RuntimeError):
    """Raised when required configuration is missing."""


def get_base_url() -> str:
    """Return the YouGile API base URL (no trailing slash)."""
    return os.environ.get(BASE_URL_ENV, DEFAULT_BASE_URL).rstrip("/")


def get_api_key() -> str:
    """Return the YouGile Bearer API key, or raise a helpful error.

    The key is created in the YouGile UI / via ``POST /api-v2/auth/keys`` and
    must be provided through the ``YOUGILE_API_KEY`` environment variable.
    """
    key = os.environ.get(API_KEY_ENV)
    if not key:
        raise ConfigError(
            f"{API_KEY_ENV} is not set. Create an API key in YouGile "
            f"(Settings -> API, or POST /api-v2/auth/keys) and export it as "
            f"{API_KEY_ENV}."
        )
    return key
