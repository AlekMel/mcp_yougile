# yougile-mcp

An [MCP](https://modelcontextprotocol.io) server that exposes the
[YouGile](https://ru.yougile.com) task-tracker API (v2) to LLM agents such as
Claude. It wraps the REST API in a curated set of well-described tools for
managing projects, boards, columns, tasks, users, chats, stickers, webhooks and
CRM contacts.

## Requirements

- Python 3.10+
- A YouGile API key (Bearer token)

## Installation

```bash
pip install -e .
# or, for development (tests):
pip install -e ".[dev]"
```

This installs a console script: `yougile-mcp`.

## Configuration

The server reads two environment variables:

| Variable           | Required | Default                  | Description                          |
| ------------------ | -------- | ------------------------ | ------------------------------------ |
| `YOUGILE_API_KEY`  | yes      | —                        | YouGile Bearer API key.              |
| `YOUGILE_BASE_URL` | no       | `https://ru.yougile.com` | Override the API host if needed.     |

### Getting an API key

Create a key in the YouGile web app (**Settings → API keys**), or call
`POST /api-v2/auth/keys` with your `login`, `password` and `companyId`
(see the YouGile API docs). Then export it:

```bash
export YOUGILE_API_KEY="your-key-here"   # PowerShell: $env:YOUGILE_API_KEY="..."
```

## Running

```bash
yougile-mcp
```

The server speaks the MCP **stdio** transport, so it is normally launched by an
MCP client rather than run by hand.

### Connect to Claude Code / Claude Desktop

Add an entry to your MCP client config (e.g. `.mcp.json` for Claude Code or
`claude_desktop_config.json` for Claude Desktop):

```json
{
  "mcpServers": {
    "yougile": {
      "command": "yougile-mcp",
      "env": {
        "YOUGILE_API_KEY": "your-key-here"
      }
    }
  }
}
```

If the script is not on `PATH`, use the absolute path or
`"command": "python", "args": ["-m", "yougile_mcp.server"]`.

## Tools

Tools are grouped by entity and prefixed with `yougile_`:

- **Tasks** — `list_tasks`, `get_task`, `create_task`, `update_task`,
  `get_task_chat_subscribers`, `update_task_chat_subscribers`
- **Projects & roles** — `list_projects`, `get_project`, `create_project`,
  `update_project`, `list_project_roles`, `get_project_role`,
  `create_project_role`, `update_project_role`, `delete_project_role`
- **Boards** — `list_boards`, `get_board`, `create_board`, `update_board`
- **Columns** — `list_columns`, `get_column`, `create_column`, `update_column`
- **Users** — `list_users`, `get_current_user`, `get_user`, `invite_user`,
  `update_user`, `delete_user`
- **Departments** — `list_departments`, `get_department`, `create_department`,
  `update_department`
- **Stickers** — `list_stickers`, `get_sticker`, `create_sticker`,
  `update_sticker`, `get_sticker_state`, `create_sticker_state`,
  `update_sticker_state` (string & sprint via a `sticker_type` argument)
- **Chats** — `list_group_chats`, `get_group_chat`, `create_group_chat`,
  `update_group_chat`, `list_chat_messages`, `get_chat_message`,
  `send_chat_message`, `update_chat_message`
- **Webhooks** — `list_webhooks`, `create_webhook`, `update_webhook`
- **Misc** — `upload_file`, `create_crm_contact`,
  `find_crm_contact_by_external_id`

All list tools support `limit`/`offset` pagination and an `include_deleted`
flag, and return the raw YouGile `{ "content": [...], "paging": {...} }` shape.

## Development

```bash
pip install -e ".[dev]"
pytest
```

Test the server interactively with the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector yougile-mcp
```


----------