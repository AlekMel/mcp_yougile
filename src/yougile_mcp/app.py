"""Shared FastMCP application instance.

Defined in its own module so tool modules can import ``mcp`` without creating a
circular import with ``server.py``.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("yougile_mcp")

# Common annotation presets reused across tools.
READ_ONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}
CREATE = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": True,
}
UPDATE = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}
DELETE = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
}
