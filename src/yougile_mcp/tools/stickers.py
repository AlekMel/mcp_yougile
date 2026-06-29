"""Sticker tools (string & sprint stickers and their states).

String and sprint stickers share an almost identical endpoint shape, so they
are unified here behind a ``sticker_type`` discriminator to keep the tool count
manageable.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import Field

from ..app import CREATE, READ_ONLY, UPDATE, mcp
from ..client import call_api
from ..models import Pagination, StrictModel


class StickerType(str, Enum):
    STRING = "string"
    SPRINT = "sprint"


def _base(sticker_type: StickerType) -> str:
    return "/api-v2/string-stickers" if sticker_type is StickerType.STRING else "/api-v2/sprint-stickers"


class ListStickersInput(Pagination):
    sticker_type: StickerType = Field(..., description="'string' or 'sprint'.")
    name: Optional[str] = Field(default=None, description="Filter by sticker name (substring).")
    board_id: Optional[str] = Field(default=None, description="Only stickers on this board id.")


class StickerIdInput(StrictModel):
    sticker_type: StickerType = Field(..., description="'string' or 'sprint'.")
    sticker_id: str = Field(..., description="Sticker id.", min_length=1)


class CreateStickerInput(StrictModel):
    sticker_type: StickerType = Field(..., description="'string' or 'sprint'.")
    name: str = Field(..., description="Sticker name.", min_length=1)
    icon: Optional[str] = Field(default=None, description="Sticker icon (string stickers only).")


class UpdateStickerInput(StickerIdInput):
    deleted: Optional[bool] = Field(default=None, description="Set true to soft-delete.")
    name: Optional[str] = Field(default=None, description="New sticker name.")
    icon: Optional[str] = Field(default=None, description="New icon (string stickers only).")


class StickerStateIdInput(StrictModel):
    sticker_type: StickerType = Field(..., description="'string' or 'sprint'.")
    sticker_id: str = Field(..., description="Parent sticker id.", min_length=1)
    state_id: str = Field(..., description="Sticker state id.", min_length=1)


class CreateStickerStateInput(StrictModel):
    sticker_type: StickerType = Field(..., description="'string' or 'sprint'.")
    sticker_id: str = Field(..., description="Parent sticker id.", min_length=1)
    name: str = Field(..., description="State name.", min_length=1)
    color: Optional[str] = Field(default=None, description="State color (string stickers).")
    begin: Optional[int] = Field(default=None, description="Sprint start, unix seconds (sprint stickers).")
    end: Optional[int] = Field(default=None, description="Sprint end, unix seconds (sprint stickers).")


class UpdateStickerStateInput(StickerStateIdInput):
    deleted: Optional[bool] = Field(default=None, description="Set true to soft-delete.")
    name: Optional[str] = Field(default=None, description="New state name.")
    color: Optional[str] = Field(default=None, description="State color (string stickers).")
    begin: Optional[int] = Field(default=None, description="Sprint start, unix seconds.")
    end: Optional[int] = Field(default=None, description="Sprint end, unix seconds.")


@mcp.tool(name="yougile_list_stickers", annotations={"title": "List stickers", **READ_ONLY})
async def list_stickers(params: ListStickersInput) -> str:
    """List string or sprint stickers, optionally filtered by board or name."""
    return await call_api(
        "GET",
        _base(params.sticker_type),
        params=params.list_params(name=params.name, boardId=params.board_id),
    )


@mcp.tool(name="yougile_get_sticker", annotations={"title": "Get sticker by id", **READ_ONLY})
async def get_sticker(params: StickerIdInput) -> str:
    """Get a single string or sprint sticker by id."""
    return await call_api("GET", f"{_base(params.sticker_type)}/{params.sticker_id}")


@mcp.tool(name="yougile_create_sticker", annotations={"title": "Create sticker", **CREATE})
async def create_sticker(params: CreateStickerInput) -> str:
    """Create a string or sprint sticker. Returns ``{"id": "<new sticker id>"}``."""
    body = params.model_dump(exclude_none=True, exclude={"sticker_type"})
    return await call_api("POST", _base(params.sticker_type), json_body=body)


@mcp.tool(name="yougile_update_sticker", annotations={"title": "Update sticker", **UPDATE})
async def update_sticker(params: UpdateStickerInput) -> str:
    """Update a string or sprint sticker (name/icon/deleted)."""
    body = params.model_dump(exclude_none=True, exclude={"sticker_type", "sticker_id"})
    return await call_api(
        "PUT", f"{_base(params.sticker_type)}/{params.sticker_id}", json_body=body
    )


@mcp.tool(name="yougile_get_sticker_state", annotations={"title": "Get sticker state", **READ_ONLY})
async def get_sticker_state(params: StickerStateIdInput) -> str:
    """Get a single sticker state by id."""
    return await call_api(
        "GET", f"{_base(params.sticker_type)}/{params.sticker_id}/states/{params.state_id}"
    )


@mcp.tool(name="yougile_create_sticker_state", annotations={"title": "Create sticker state", **CREATE})
async def create_sticker_state(params: CreateStickerStateInput) -> str:
    """Add a state to a string sticker (name/color) or sprint sticker (name/begin/end)."""
    body = params.model_dump(exclude_none=True, exclude={"sticker_type", "sticker_id"})
    return await call_api(
        "POST", f"{_base(params.sticker_type)}/{params.sticker_id}/states", json_body=body
    )


@mcp.tool(name="yougile_update_sticker_state", annotations={"title": "Update sticker state", **UPDATE})
async def update_sticker_state(params: UpdateStickerStateInput) -> str:
    """Update a sticker state (name/color or begin/end, or deleted flag)."""
    body = params.model_dump(
        exclude_none=True, exclude={"sticker_type", "sticker_id", "state_id"}
    )
    return await call_api(
        "PUT",
        f"{_base(params.sticker_type)}/{params.sticker_id}/states/{params.state_id}",
        json_body=body,
    )
