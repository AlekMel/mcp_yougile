"""Tests for tool registration and endpoint mapping."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

import yougile_mcp.server as server
from yougile_mcp.tools import boards, stickers, tasks

BASE = "https://api.test"


async def test_all_tools_registered():
    tools = await server.mcp.list_tools()
    names = {t.name for t in tools}
    assert len(tools) >= 50
    # A representative sample across modules.
    for name in [
        "yougile_list_tasks",
        "yougile_create_task",
        "yougile_update_task",
        "yougile_list_projects",
        "yougile_delete_project_role",
        "yougile_send_chat_message",
        "yougile_upload_file",
    ]:
        assert name in names


async def test_every_tool_has_annotations_and_unique_names():
    tools = await server.mcp.list_tools()
    names = [t.name for t in tools]
    assert len(names) == len(set(names)), "tool names must be unique"
    for t in tools:
        assert t.name.startswith("yougile_")
        assert t.annotations is not None


@respx.mock
async def test_list_tasks_uses_task_list_endpoint_with_filters():
    route = respx.get(f"{BASE}/api-v2/task-list").mock(
        return_value=httpx.Response(200, json={"content": [], "paging": {}})
    )
    await tasks.list_tasks(tasks.ListTasksInput(column_id="c1", limit=10))

    url = route.calls.last.request.url
    assert url.params["columnId"] == "c1"
    assert url.params["limit"] == "10"
    assert url.params["offset"] == "0"


@respx.mock
async def test_list_tasks_reversed_uses_tasks_endpoint():
    route = respx.get(f"{BASE}/api-v2/tasks").mock(
        return_value=httpx.Response(200, json={"content": []})
    )
    await tasks.list_tasks(tasks.ListTasksInput(reversed=True))
    assert route.called


@respx.mock
async def test_create_task_maps_camel_case_body():
    route = respx.post(f"{BASE}/api-v2/tasks").mock(
        return_value=httpx.Response(200, json={"id": "t1"})
    )
    result = await tasks.create_task(
        tasks.CreateTaskInput(title="T", column_id="c1", idempotency_key="k1")
    )

    body = json.loads(route.calls.last.request.content)
    assert body == {"title": "T", "columnId": "c1", "idempotencyKey": "k1"}
    assert json.loads(result) == {"id": "t1"}


@respx.mock
async def test_create_board_renames_project_id():
    route = respx.post(f"{BASE}/api-v2/boards").mock(
        return_value=httpx.Response(200, json={"id": "b1"})
    )
    await boards.create_board(boards.CreateBoardInput(title="B", project_id="p1"))
    body = json.loads(route.calls.last.request.content)
    assert body == {"title": "B", "projectId": "p1"}


@respx.mock
async def test_sticker_type_selects_endpoint():
    route = respx.get(f"{BASE}/api-v2/sprint-stickers").mock(
        return_value=httpx.Response(200, json={"content": []})
    )
    await stickers.list_stickers(
        stickers.ListStickersInput(sticker_type=stickers.StickerType.SPRINT)
    )
    assert route.called


async def test_invalid_email_is_rejected():
    from yougile_mcp.tools import users

    with pytest.raises(Exception):
        users.InviteUserInput(email="not-an-email")
