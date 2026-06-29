"""User tools for the YouGile MCP server."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from ..app import CREATE, DELETE, READ_ONLY, UPDATE, mcp
from ..client import call_api
from ..models import Pagination, StrictModel


class ListUsersInput(Pagination):
    email: Optional[str] = Field(default=None, description="Filter by email (substring).")
    project_id: Optional[str] = Field(
        default=None, description="Only users that are members of this project id."
    )


class UserIdInput(StrictModel):
    user_id: str = Field(..., description="User id.", min_length=1)


class InviteUserInput(StrictModel):
    email: str = Field(
        ..., description="Email of the person to invite.",
        pattern=r"^[\w.+-]+@[\w-]+\.[\w.-]+$",
    )
    is_admin: Optional[bool] = Field(default=None, description="Grant admin rights.")


class UpdateUserInput(UserIdInput):
    is_admin: Optional[bool] = Field(default=None, description="Set admin rights for the user.")


@mcp.tool(name="yougile_list_users", annotations={"title": "List users", **READ_ONLY})
async def list_users(params: ListUsersInput) -> str:
    """List users in the company, optionally filtered by email or project membership."""
    return await call_api(
        "GET",
        "/api-v2/users",
        params=params.list_params(email=params.email, projectId=params.project_id),
    )


@mcp.tool(name="yougile_get_current_user", annotations={"title": "Get current user", **READ_ONLY})
async def get_current_user() -> str:
    """Get the user that owns the current API key (the authenticated account)."""
    return await call_api("GET", "/api-v2/users/me")


@mcp.tool(name="yougile_get_user", annotations={"title": "Get user by id", **READ_ONLY})
async def get_user(params: UserIdInput) -> str:
    """Get a single company user by id."""
    return await call_api("GET", f"/api-v2/users/{params.user_id}")


@mcp.tool(name="yougile_invite_user", annotations={"title": "Invite user", **CREATE})
async def invite_user(params: InviteUserInput) -> str:
    """Invite a person to the company by email. Returns the created/invited user id."""
    body: dict[str, object] = {"email": params.email}
    if params.is_admin is not None:
        body["isAdmin"] = params.is_admin
    return await call_api("POST", "/api-v2/users", json_body=body)


@mcp.tool(name="yougile_update_user", annotations={"title": "Update user", **UPDATE})
async def update_user(params: UpdateUserInput) -> str:
    """Update a company user (e.g. toggle admin rights)."""
    body: dict[str, object] = {}
    if params.is_admin is not None:
        body["isAdmin"] = params.is_admin
    return await call_api("PUT", f"/api-v2/users/{params.user_id}", json_body=body)


@mcp.tool(name="yougile_delete_user", annotations={"title": "Remove user from company", **DELETE})
async def delete_user(params: UserIdInput) -> str:
    """Remove a user from the company by id."""
    return await call_api("DELETE", f"/api-v2/users/{params.user_id}")
