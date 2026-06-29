"""Column tools for the YouGile MCP server."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from ..app import CREATE, READ_ONLY, UPDATE, mcp
from ..client import call_api
from ..models import Pagination, StrictModel


class ListColumnsInput(Pagination):
    title: Optional[str] = Field(default=None, description="Filter by column title (substring).")
    board_id: Optional[str] = Field(default=None, description="Only columns in this board id.")


class ColumnIdInput(StrictModel):
    column_id: str = Field(..., description="Column id.", min_length=1)


class CreateColumnInput(StrictModel):
    title: str = Field(..., description="Column title.", min_length=1)
    board_id: str = Field(..., description="Board id the column belongs to.", min_length=1)
    color: Optional[int] = Field(default=None, description="Column color as a number (1-16).")


class UpdateColumnInput(ColumnIdInput):
    deleted: Optional[bool] = Field(default=None, description="Set true to soft-delete.")
    title: Optional[str] = Field(default=None, description="New title.")
    board_id: Optional[str] = Field(default=None, description="Move to this board id.")
    color: Optional[int] = Field(default=None, description="Column color as a number (1-16).")


@mcp.tool(name="yougile_list_columns", annotations={"title": "List columns", **READ_ONLY})
async def list_columns(params: ListColumnsInput) -> str:
    """List columns, optionally filtered by board or title."""
    return await call_api(
        "GET",
        "/api-v2/columns",
        params=params.list_params(title=params.title, boardId=params.board_id),
    )


@mcp.tool(name="yougile_get_column", annotations={"title": "Get column by id", **READ_ONLY})
async def get_column(params: ColumnIdInput) -> str:
    """Get a single column by id."""
    return await call_api("GET", f"/api-v2/columns/{params.column_id}")


@mcp.tool(name="yougile_create_column", annotations={"title": "Create column", **CREATE})
async def create_column(params: CreateColumnInput) -> str:
    """Create a column on a board. Returns ``{"id": "<new column id>"}``."""
    body = params.model_dump(exclude_none=True)
    body["boardId"] = body.pop("board_id")
    return await call_api("POST", "/api-v2/columns", json_body=body)


@mcp.tool(name="yougile_update_column", annotations={"title": "Update column", **UPDATE})
async def update_column(params: UpdateColumnInput) -> str:
    """Update a column's title, board, color or deleted flag. Only provided fields change."""
    body = params.model_dump(exclude_none=True, exclude={"column_id"})
    if "board_id" in body:
        body["boardId"] = body.pop("board_id")
    return await call_api("PUT", f"/api-v2/columns/{params.column_id}", json_body=body)
