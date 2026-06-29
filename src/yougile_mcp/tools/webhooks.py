"""Webhook subscription tools for the YouGile MCP server."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from ..app import CREATE, READ_ONLY, UPDATE, mcp
from ..client import call_api
from ..models import StrictModel


class ListWebhooksInput(StrictModel):
    include_deleted: bool = Field(default=False, description="Include deleted subscriptions.")


class CreateWebhookInput(StrictModel):
    url: str = Field(..., description="Callback URL to receive events.", min_length=1)
    event: str = Field(
        ...,
        description="Event to subscribe to, e.g. 'task-created', 'task-moved', '*' for all.",
        min_length=1,
    )
    filters: Optional[list[dict[str, Any]]] = Field(
        default=None, description="Additional event filters."
    )


class UpdateWebhookInput(StrictModel):
    webhook_id: str = Field(..., description="Webhook subscription id.", min_length=1)
    url: Optional[str] = Field(default=None, description="New callback URL.")
    event: Optional[str] = Field(default=None, description="New event name.")
    disabled: Optional[bool] = Field(default=None, description="If true, the webhook won't fire.")
    deleted: Optional[bool] = Field(default=None, description="Set true to delete the subscription.")
    filters: Optional[list[dict[str, Any]]] = Field(default=None, description="New event filters.")


@mcp.tool(name="yougile_list_webhooks", annotations={"title": "List webhooks", **READ_ONLY})
async def list_webhooks(params: ListWebhooksInput) -> str:
    """List webhook subscriptions for the company."""
    return await call_api(
        "GET", "/api-v2/webhooks", params={"includeDeleted": params.include_deleted}
    )


@mcp.tool(name="yougile_create_webhook", annotations={"title": "Create webhook", **CREATE})
async def create_webhook(params: CreateWebhookInput) -> str:
    """Create a webhook subscription. Returns ``{"id": "<new webhook id>"}``."""
    body: dict[str, Any] = {"url": params.url, "event": params.event}
    body["filters"] = params.filters if params.filters is not None else []
    return await call_api("POST", "/api-v2/webhooks", json_body=body)


@mcp.tool(name="yougile_update_webhook", annotations={"title": "Update webhook", **UPDATE})
async def update_webhook(params: UpdateWebhookInput) -> str:
    """Update a webhook subscription (url, event, disabled, filters or deleted)."""
    body = params.model_dump(exclude_none=True, exclude={"webhook_id"})
    return await call_api("PUT", f"/api-v2/webhooks/{params.webhook_id}", json_body=body)
