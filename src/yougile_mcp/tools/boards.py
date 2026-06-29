"""Board tools for the YouGile MCP server."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from ..app import CREATE, READ_ONLY, UPDATE, mcp
from ..client import call_api
from ..models import Pagination, StrictModel


class ListBoardsInput(Pagination):
    title: Optional[str] = Field(default=None, description="Filter by board title (substring).")
    project_id: Optional[str] = Field(default=None, description="Only boards in this project id.")


class BoardIdInput(StrictModel):
    board_id: str = Field(..., description="Board id.", min_length=1)


class CreateBoardInput(StrictModel):
    title: str = Field(..., description="Board title.", min_length=1)
    project_id: str = Field(..., description="Project id the board belongs to.", min_length=1)
    stickers: Optional[dict[str, Any]] = Field(default=None, description="Board stickers config.")


class UpdateBoardInput(BoardIdInput):
    deleted: Optional[bool] = Field(default=None, description="Set true to soft-delete.")
    title: Optional[str] = Field(default=None, description="New title.")
    project_id: Optional[str] = Field(default=None, description="Move to this project id.")
    stickers: Optional[dict[str, Any]] = Field(default=None, description="Board stickers config.")


@mcp.tool(name="yougile_list_boards", annotations={"title": "List boards", **READ_ONLY})
async def list_boards(params: ListBoardsInput) -> str:
    """List boards, optionally filtered by project or title."""
    return await call_api(
        "GET",
        "/api-v2/boards",
        params=params.list_params(title=params.title, projectId=params.project_id),
    )


@mcp.tool(name="yougile_get_board", annotations={"title": "Get board by id", **READ_ONLY})
async def get_board(params: BoardIdInput) -> str:
    """Get a single board by id."""
    return await call_api("GET", f"/api-v2/boards/{params.board_id}")


@mcp.tool(name="yougile_create_board", annotations={"title": "Create board", **CREATE})
async def create_board(params: CreateBoardInput) -> str:
    """Create a board in a project. Returns ``{"id": "<new board id>"}``."""
    body = params.model_dump(exclude_none=True)
    body["projectId"] = body.pop("project_id")
    return await call_api("POST", "/api-v2/boards", json_body=body)


@mcp.tool(name="yougile_update_board", annotations={"title": "Update board", **UPDATE})
async def update_board(params: UpdateBoardInput) -> str:
    """Update a board's title, project or deleted flag. Only provided fields change."""
    body = params.model_dump(exclude_none=True, exclude={"board_id"})
    if "project_id" in body:
        body["projectId"] = body.pop("project_id")
    return await call_api("PUT", f"/api-v2/boards/{params.board_id}", json_body=body)
