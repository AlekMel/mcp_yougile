"""Entry point for the YouGile MCP server.

Importing the tool modules registers every tool on the shared ``mcp`` instance
via the ``@mcp.tool`` decorator. ``main()`` then starts the stdio transport.
"""

from __future__ import annotations

from .app import mcp

# Import tool modules for their registration side effects.
from .tools import (  # noqa: F401  (imported for @mcp.tool side effects)
    boards,
    chats,
    columns,
    departments,
    misc,
    projects,
    stickers,
    tasks,
    users,
    webhooks,
)


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
