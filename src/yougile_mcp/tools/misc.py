"""Miscellaneous tools: file upload and CRM contacts."""

from __future__ import annotations

import os
from typing import Any, Optional

from pydantic import Field

from ..app import CREATE, READ_ONLY, mcp
from ..client import call_api, call_api_upload
from ..models import StrictModel


class UploadFileInput(StrictModel):
    file_path: str = Field(
        ..., description="Absolute path to a local file to upload to YouGile.", min_length=1
    )


class CreateCrmContactInput(StrictModel):
    project_id: str = Field(..., description="CRM project id where the contact is created.", min_length=1)
    title: str = Field(..., description="Contact person name/title.", min_length=1)
    fields: Optional[dict[str, Any]] = Field(default=None, description="Custom contact fields.")


class FindCrmContactInput(StrictModel):
    provider: str = Field(..., description="External provider name.", min_length=1)
    chat_id: str = Field(..., description="External chat id to look up.", min_length=1)


@mcp.tool(name="yougile_upload_file", annotations={"title": "Upload file", **CREATE})
async def upload_file(params: UploadFileInput) -> str:
    """Upload a local file to YouGile. Returns the uploaded file metadata/URL.

    The file is read from ``file_path`` on the machine running this server.
    """
    if not os.path.isfile(params.file_path):
        return f"Error: file not found at {params.file_path}"
    with open(params.file_path, "rb") as fh:
        content = fh.read()
    return await call_api_upload(
        "/api-v2/upload-file", filename=os.path.basename(params.file_path), content=content
    )


@mcp.tool(name="yougile_create_crm_contact", annotations={"title": "Create CRM contact", **CREATE})
async def create_crm_contact(params: CreateCrmContactInput) -> str:
    """Create a CRM contact person in a CRM project. Returns the created contact id."""
    body: dict[str, Any] = {"projectId": params.project_id, "title": params.title}
    if params.fields is not None:
        body["fields"] = params.fields
    return await call_api("POST", "/api-v2/crm/contact-persons", json_body=body)


@mcp.tool(
    name="yougile_find_crm_contact_by_external_id",
    annotations={"title": "Find CRM contact by external id", **READ_ONLY},
)
async def find_crm_contact_by_external_id(params: FindCrmContactInput) -> str:
    """Find a CRM contact by an external provider and chat id."""
    return await call_api(
        "GET",
        "/api-v2/crm/contacts/by-external-id",
        params={"provider": params.provider, "chatId": params.chat_id},
    )
