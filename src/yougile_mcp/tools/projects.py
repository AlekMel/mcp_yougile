"""Project and project-role tools for the YouGile MCP server."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from ..app import CREATE, DELETE, READ_ONLY, UPDATE, mcp
from ..client import call_api
from ..models import Pagination, StrictModel


class ListProjectsInput(Pagination):
    title: Optional[str] = Field(default=None, description="Filter by project title (substring).")


class ProjectIdInput(StrictModel):
    project_id: str = Field(..., description="Project id.", min_length=1)


class CreateProjectInput(StrictModel):
    title: str = Field(..., description="Project title.", min_length=1)
    users: Optional[dict[str, str]] = Field(
        default=None,
        description="Map of {userId: role}. Role is a role id or 'admin'/'worker'/'observer'.",
    )


class UpdateProjectInput(ProjectIdInput):
    deleted: Optional[bool] = Field(default=None, description="Set true to soft-delete.")
    title: Optional[str] = Field(default=None, description="New title.")
    users: Optional[dict[str, str]] = Field(
        default=None, description="Map of {userId: role}; '-' as role removes the user."
    )


class ListProjectRolesInput(Pagination):
    project_id: str = Field(..., description="Project id.", min_length=1)
    name: Optional[str] = Field(default=None, description="Filter by role name (substring).")


class ProjectRoleIdInput(StrictModel):
    project_id: str = Field(..., description="Project id.", min_length=1)
    role_id: str = Field(..., description="Role id.", min_length=1)


class CreateProjectRoleInput(StrictModel):
    project_id: str = Field(..., description="Project id.", min_length=1)
    name: str = Field(..., description="Role name.", min_length=1)
    permissions: dict[str, Any] = Field(..., description="Permissions object for the role.")
    description: Optional[str] = Field(default=None, description="Role description.")


class UpdateProjectRoleInput(ProjectRoleIdInput):
    name: Optional[str] = Field(default=None, description="New role name.")
    permissions: Optional[dict[str, Any]] = Field(default=None, description="Permissions object.")
    description: Optional[str] = Field(default=None, description="Role description.")


@mcp.tool(name="yougile_list_projects", annotations={"title": "List projects", **READ_ONLY})
async def list_projects(params: ListProjectsInput) -> str:
    """List projects. Returns ``content`` (array) and ``paging`` metadata."""
    return await call_api(
        "GET", "/api-v2/projects", params=params.list_params(title=params.title)
    )


@mcp.tool(name="yougile_get_project", annotations={"title": "Get project by id", **READ_ONLY})
async def get_project(params: ProjectIdInput) -> str:
    """Get a single project by id."""
    return await call_api("GET", f"/api-v2/projects/{params.project_id}")


@mcp.tool(name="yougile_create_project", annotations={"title": "Create project", **CREATE})
async def create_project(params: CreateProjectInput) -> str:
    """Create a project. Returns ``{"id": "<new project id>"}``."""
    return await call_api("POST", "/api-v2/projects", json_body=params.model_dump(exclude_none=True))


@mcp.tool(name="yougile_update_project", annotations={"title": "Update project", **UPDATE})
async def update_project(params: UpdateProjectInput) -> str:
    """Update a project's title, members or deleted flag. Only provided fields change."""
    body = params.model_dump(exclude_none=True, exclude={"project_id"})
    return await call_api("PUT", f"/api-v2/projects/{params.project_id}", json_body=body)


@mcp.tool(name="yougile_list_project_roles", annotations={"title": "List project roles", **READ_ONLY})
async def list_project_roles(params: ListProjectRolesInput) -> str:
    """List roles defined in a project."""
    return await call_api(
        "GET",
        f"/api-v2/projects/{params.project_id}/roles",
        params=params.list_params(name=params.name),
    )


@mcp.tool(name="yougile_get_project_role", annotations={"title": "Get project role", **READ_ONLY})
async def get_project_role(params: ProjectRoleIdInput) -> str:
    """Get a single project role by id."""
    return await call_api(
        "GET", f"/api-v2/projects/{params.project_id}/roles/{params.role_id}"
    )


@mcp.tool(name="yougile_create_project_role", annotations={"title": "Create project role", **CREATE})
async def create_project_role(params: CreateProjectRoleInput) -> str:
    """Create a role in a project. Returns ``{"id": "<new role id>"}``."""
    body = params.model_dump(exclude_none=True, exclude={"project_id"})
    return await call_api(
        "POST", f"/api-v2/projects/{params.project_id}/roles", json_body=body
    )


@mcp.tool(name="yougile_update_project_role", annotations={"title": "Update project role", **UPDATE})
async def update_project_role(params: UpdateProjectRoleInput) -> str:
    """Update a project role. Only provided fields change."""
    body = params.model_dump(exclude_none=True, exclude={"project_id", "role_id"})
    return await call_api(
        "PUT", f"/api-v2/projects/{params.project_id}/roles/{params.role_id}", json_body=body
    )


@mcp.tool(name="yougile_delete_project_role", annotations={"title": "Delete project role", **DELETE})
async def delete_project_role(params: ProjectRoleIdInput) -> str:
    """Delete a project role by id."""
    return await call_api(
        "DELETE", f"/api-v2/projects/{params.project_id}/roles/{params.role_id}"
    )
