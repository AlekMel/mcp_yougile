"""Task tools for the YouGile MCP server."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from ..app import CREATE, READ_ONLY, UPDATE, mcp
from ..client import call_api
from ..models import Pagination, StrictModel, rename_keys


class ListTasksInput(Pagination):
    """Filters for listing tasks."""

    title: Optional[str] = Field(default=None, description="Filter by task title (substring).")
    column_id: Optional[str] = Field(default=None, description="Only tasks in this column id.")
    assigned_to: Optional[str] = Field(default=None, description="Only tasks assigned to this user id.")
    sticker_id: Optional[str] = Field(default=None, description="Only tasks having this sticker id.")
    sticker_state_id: Optional[str] = Field(
        default=None, description="Only tasks in this sticker state id."
    )
    reversed: bool = Field(
        default=False,
        description="If true, return newest-first (GET /tasks); otherwise oldest-first (GET /task-list).",
    )


class TaskIdInput(StrictModel):
    task_id: str = Field(..., description="Task id.", min_length=1)


class CreateTaskInput(StrictModel):
    """Fields for creating a task (maps to CreateTaskDto)."""

    title: str = Field(..., description="Task title.", min_length=1)
    column_id: Optional[str] = Field(default=None, description="Parent column id.")
    description: Optional[str] = Field(default=None, description="Task description.")
    archived: Optional[bool] = Field(default=None, description="Whether the task is archived.")
    completed: Optional[bool] = Field(default=None, description="Whether the task is completed.")
    subtasks: Optional[list[str]] = Field(default=None, description="Array of subtask ids.")
    assigned: Optional[list[str]] = Field(default=None, description="Array of assignee user ids.")
    color: Optional[str] = Field(
        default=None,
        description="Card color, e.g. 'task-primary', 'task-red', 'task-green'.",
    )
    stickers: Optional[dict[str, Any]] = Field(
        default=None, description="Custom stickers as a {stickerId: stateId} map."
    )
    deadline: Optional[dict[str, Any]] = Field(default=None, description="Deadline sticker object.")
    time_tracking: Optional[dict[str, Any]] = Field(
        default=None, description="Time-tracking sticker object."
    )
    idempotency_key: Optional[str] = Field(
        default=None, description="Idempotency key: repeating it returns the same task."
    )


class UpdateTaskInput(TaskIdInput):
    """Fields for updating a task (maps to UpdateTaskDto). Omit to leave unchanged."""

    deleted: Optional[bool] = Field(default=None, description="Set true to soft-delete the task.")
    title: Optional[str] = Field(default=None, description="New title.")
    column_id: Optional[str] = Field(
        default=None, description="Move to this column id (null/'-' removes from column)."
    )
    description: Optional[str] = Field(default=None, description="New description.")
    archived: Optional[bool] = Field(default=None, description="Archive flag.")
    completed: Optional[bool] = Field(default=None, description="Completion flag.")
    subtasks: Optional[list[str]] = Field(default=None, description="Array of subtask ids.")
    assigned: Optional[list[str]] = Field(default=None, description="Array of assignee user ids.")
    color: Optional[str] = Field(default=None, description="Card color.")
    stickers: Optional[dict[str, Any]] = Field(
        default=None, description="Custom stickers as a {stickerId: stateId} map."
    )
    deadline: Optional[dict[str, Any]] = Field(default=None, description="Deadline sticker object.")
    time_tracking: Optional[dict[str, Any]] = Field(
        default=None, description="Time-tracking sticker object."
    )


class ChatSubscribersInput(TaskIdInput):
    subscribers: list[str] = Field(
        ..., description="Full list of user ids subscribed to the task chat."
    )


@mcp.tool(name="yougile_list_tasks", annotations={"title": "List tasks", **READ_ONLY})
async def list_tasks(params: ListTasksInput) -> str:
    """List tasks, with optional filters by column, assignee, sticker or title.

    Returns a JSON object with ``content`` (array of tasks) and ``paging``
    metadata. Use ``reversed=true`` for newest-first ordering.
    """
    path = "/api-v2/tasks" if params.reversed else "/api-v2/task-list"
    query = params.list_params(
        title=params.title,
        columnId=params.column_id,
        assignedTo=params.assigned_to,
        stickerId=params.sticker_id,
        stickerStateId=params.sticker_state_id,
    )
    return await call_api("GET", path, params=query)


@mcp.tool(name="yougile_get_task", annotations={"title": "Get task by id", **READ_ONLY})
async def get_task(params: TaskIdInput) -> str:
    """Get a single task by its id. Returns the full task JSON object."""
    return await call_api("GET", f"/api-v2/tasks/{params.task_id}")


@mcp.tool(name="yougile_create_task", annotations={"title": "Create task", **CREATE})
async def create_task(params: CreateTaskInput) -> str:
    """Create a task in a column. Returns ``{"id": "<new task id>"}``."""
    body = params.model_dump(exclude_none=True)
    rename_keys(body, {"column_id": "columnId", "time_tracking": "timeTracking",
                       "idempotency_key": "idempotencyKey"})
    return await call_api("POST", "/api-v2/tasks", json_body=body)


@mcp.tool(name="yougile_update_task", annotations={"title": "Update task", **UPDATE})
async def update_task(params: UpdateTaskInput) -> str:
    """Update a task: title, column, completion, assignees, stickers, etc.

    Only provided fields are changed. Set ``deleted=true`` to soft-delete.
    """
    body = params.model_dump(exclude_none=True, exclude={"task_id"})
    rename_keys(body, {"column_id": "columnId", "time_tracking": "timeTracking"})
    return await call_api("PUT", f"/api-v2/tasks/{params.task_id}", json_body=body)


@mcp.tool(
    name="yougile_get_task_chat_subscribers",
    annotations={"title": "Get task chat subscribers", **READ_ONLY},
)
async def get_task_chat_subscribers(params: TaskIdInput) -> str:
    """List the user ids subscribed to a task's chat."""
    return await call_api("GET", f"/api-v2/tasks/{params.task_id}/chat-subscribers")


@mcp.tool(
    name="yougile_update_task_chat_subscribers",
    annotations={"title": "Set task chat subscribers", **UPDATE},
)
async def update_task_chat_subscribers(params: ChatSubscribersInput) -> str:
    """Replace the list of subscribers of a task's chat with the given user ids."""
    return await call_api(
        "PUT",
        f"/api-v2/tasks/{params.task_id}/chat-subscribers",
        json_body={"content": params.subscribers},
    )
