"""Department tools for the YouGile MCP server."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from ..app import CREATE, READ_ONLY, UPDATE, mcp
from ..client import call_api
from ..models import Pagination, StrictModel


class ListDepartmentsInput(Pagination):
    title: Optional[str] = Field(default=None, description="Filter by department title (substring).")
    parent_id: Optional[str] = Field(default=None, description="Only children of this parent id.")


class DepartmentIdInput(StrictModel):
    department_id: str = Field(..., description="Department id.", min_length=1)


class CreateDepartmentInput(StrictModel):
    title: str = Field(..., description="Department title.", min_length=1)
    parent_id: Optional[str] = Field(
        default=None, description="Parent department id; omit or '-' for a top-level department."
    )
    users: Optional[dict[str, str]] = Field(
        default=None, description="Map of {userId: role} for department members."
    )


class UpdateDepartmentInput(DepartmentIdInput):
    deleted: Optional[bool] = Field(default=None, description="Set true to soft-delete.")
    title: Optional[str] = Field(default=None, description="New title.")
    parent_id: Optional[str] = Field(default=None, description="New parent department id.")
    users: Optional[dict[str, str]] = Field(
        default=None, description="Map of {userId: role}; '-' as role removes the user."
    )


@mcp.tool(name="yougile_list_departments", annotations={"title": "List departments", **READ_ONLY})
async def list_departments(params: ListDepartmentsInput) -> str:
    """List departments, optionally filtered by title or parent."""
    return await call_api(
        "GET",
        "/api-v2/departments",
        params=params.list_params(title=params.title, parentId=params.parent_id),
    )


@mcp.tool(name="yougile_get_department", annotations={"title": "Get department by id", **READ_ONLY})
async def get_department(params: DepartmentIdInput) -> str:
    """Get a single department by id."""
    return await call_api("GET", f"/api-v2/departments/{params.department_id}")


@mcp.tool(name="yougile_create_department", annotations={"title": "Create department", **CREATE})
async def create_department(params: CreateDepartmentInput) -> str:
    """Create a department. Returns ``{"id": "<new department id>"}``."""
    body = params.model_dump(exclude_none=True)
    if "parent_id" in body:
        body["parentId"] = body.pop("parent_id")
    return await call_api("POST", "/api-v2/departments", json_body=body)


@mcp.tool(name="yougile_update_department", annotations={"title": "Update department", **UPDATE})
async def update_department(params: UpdateDepartmentInput) -> str:
    """Update a department's title, parent, members or deleted flag."""
    body = params.model_dump(exclude_none=True, exclude={"department_id"})
    if "parent_id" in body:
        body["parentId"] = body.pop("parent_id")
    return await call_api("PUT", f"/api-v2/departments/{params.department_id}", json_body=body)
