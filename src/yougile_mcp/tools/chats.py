"""Group chat and chat message tools for the YouGile MCP server."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from ..app import CREATE, READ_ONLY, UPDATE, mcp
from ..client import call_api
from ..models import Pagination, StrictModel


# --- Group chats -----------------------------------------------------------

class ListGroupChatsInput(Pagination):
    title: Optional[str] = Field(default=None, description="Filter by chat title (substring).")


class GroupChatIdInput(StrictModel):
    chat_id: str = Field(..., description="Group chat id.", min_length=1)


class CreateGroupChatInput(StrictModel):
    title: str = Field(..., description="Chat title.", min_length=1)
    users: dict[str, Any] = Field(..., description="Members of the chat ({userId: ...}).")
    user_role_map: dict[str, Any] = Field(..., description="Per-user roles in the chat.")
    role_config_map: dict[str, Any] = Field(..., description="Role configuration map.")


class UpdateGroupChatInput(GroupChatIdInput):
    deleted: Optional[bool] = Field(default=None, description="Set true to soft-delete.")
    title: Optional[str] = Field(default=None, description="New chat title.")
    users: Optional[dict[str, Any]] = Field(default=None, description="Members of the chat.")
    user_role_map: Optional[dict[str, Any]] = Field(default=None, description="Per-user roles.")
    role_config_map: Optional[dict[str, Any]] = Field(default=None, description="Role config map.")


# --- Chat messages ---------------------------------------------------------

class ListMessagesInput(Pagination):
    chat_id: str = Field(..., description="Chat id (group chat or task chat).", min_length=1)
    from_user_id: Optional[str] = Field(default=None, description="Only messages from this user id.")
    text: Optional[str] = Field(default=None, description="Filter by message text (substring).")
    label: Optional[str] = Field(default=None, description="Filter by quick-link label.")
    since: Optional[int] = Field(default=None, description="Only messages after this unix-seconds time.")
    include_system: Optional[bool] = Field(default=None, description="Include system messages.")


class MessageIdInput(StrictModel):
    chat_id: str = Field(..., description="Chat id.", min_length=1)
    message_id: str = Field(..., description="Message id.", min_length=1)


class SendMessageInput(StrictModel):
    chat_id: str = Field(..., description="Chat id to post into.", min_length=1)
    text: str = Field(..., description="Plain-text message body.", min_length=1)
    text_html: Optional[str] = Field(
        default=None, description="HTML body; defaults to the plain text if omitted."
    )
    label: Optional[str] = Field(default=None, description="Quick-link label for the message.")


class UpdateMessageInput(MessageIdInput):
    deleted: Optional[bool] = Field(default=None, description="Set true to delete the message.")
    label: Optional[str] = Field(default=None, description="New quick-link label.")
    react: Optional[str] = Field(default=None, description="Admin reactions list.")


@mcp.tool(name="yougile_list_group_chats", annotations={"title": "List group chats", **READ_ONLY})
async def list_group_chats(params: ListGroupChatsInput) -> str:
    """List group chats, optionally filtered by title."""
    return await call_api(
        "GET", "/api-v2/group-chats", params=params.list_params(title=params.title)
    )


@mcp.tool(name="yougile_get_group_chat", annotations={"title": "Get group chat by id", **READ_ONLY})
async def get_group_chat(params: GroupChatIdInput) -> str:
    """Get a single group chat by id."""
    return await call_api("GET", f"/api-v2/group-chats/{params.chat_id}")


@mcp.tool(name="yougile_create_group_chat", annotations={"title": "Create group chat", **CREATE})
async def create_group_chat(params: CreateGroupChatInput) -> str:
    """Create a group chat. Returns ``{"id": "<new chat id>"}``."""
    body = {
        "title": params.title,
        "users": params.users,
        "userRoleMap": params.user_role_map,
        "roleConfigMap": params.role_config_map,
    }
    return await call_api("POST", "/api-v2/group-chats", json_body=body)


@mcp.tool(name="yougile_update_group_chat", annotations={"title": "Update group chat", **UPDATE})
async def update_group_chat(params: UpdateGroupChatInput) -> str:
    """Update a group chat (title, members, roles or deleted flag)."""
    body: dict[str, Any] = {}
    if params.deleted is not None:
        body["deleted"] = params.deleted
    if params.title is not None:
        body["title"] = params.title
    if params.users is not None:
        body["users"] = params.users
    if params.user_role_map is not None:
        body["userRoleMap"] = params.user_role_map
    if params.role_config_map is not None:
        body["roleConfigMap"] = params.role_config_map
    return await call_api("PUT", f"/api-v2/group-chats/{params.chat_id}", json_body=body)


@mcp.tool(name="yougile_list_chat_messages", annotations={"title": "List chat messages", **READ_ONLY})
async def list_chat_messages(params: ListMessagesInput) -> str:
    """List messages in a chat (group chat or a task chat), with filters."""
    return await call_api(
        "GET",
        f"/api-v2/chats/{params.chat_id}/messages",
        params=params.list_params(
            fromUserId=params.from_user_id,
            text=params.text,
            label=params.label,
            since=params.since,
            includeSystem=params.include_system,
        ),
    )


@mcp.tool(name="yougile_get_chat_message", annotations={"title": "Get chat message", **READ_ONLY})
async def get_chat_message(params: MessageIdInput) -> str:
    """Get a single chat message by id."""
    return await call_api(
        "GET", f"/api-v2/chats/{params.chat_id}/messages/{params.message_id}"
    )


@mcp.tool(name="yougile_send_chat_message", annotations={"title": "Send chat message", **CREATE})
async def send_chat_message(params: SendMessageInput) -> str:
    """Post a message into a chat. Returns the created message id."""
    body = {
        "text": params.text,
        "textHtml": params.text_html if params.text_html is not None else params.text,
        "label": params.label if params.label is not None else "",
    }
    return await call_api(
        "POST", f"/api-v2/chats/{params.chat_id}/messages", json_body=body
    )


@mcp.tool(name="yougile_update_chat_message", annotations={"title": "Update chat message", **UPDATE})
async def update_chat_message(params: UpdateMessageInput) -> str:
    """Edit a chat message: change label, add reactions, or delete it."""
    body: dict[str, Any] = {}
    if params.deleted is not None:
        body["deleted"] = params.deleted
    if params.label is not None:
        body["label"] = params.label
    if params.react is not None:
        body["react"] = params.react
    return await call_api(
        "PUT", f"/api-v2/chats/{params.chat_id}/messages/{params.message_id}", json_body=body
    )
