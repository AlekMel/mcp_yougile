"""Shared Pydantic base models and field helpers for tool inputs."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


def rename_keys(body: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
    """Rename snake_case keys to the API's camelCase names, in place.

    Returns the same dict for convenient chaining.
    """
    for src, dst in mapping.items():
        if src in body:
            body[dst] = body.pop(src)
    return body


class StrictModel(BaseModel):
    """Base input model: strip whitespace, validate on assignment, no extras."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )


class Pagination(StrictModel):
    """Mixin providing the standard YouGile list query parameters."""

    limit: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum number of items to return (max 1000).",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Index of the first item to return (for pagination).",
    )
    include_deleted: bool = Field(
        default=False,
        description="Include soft-deleted objects in the result.",
    )

    def list_params(self, **extra: object) -> dict[str, object]:
        """Build the query-param dict for a list endpoint, dropping empties."""
        params: dict[str, object] = {
            "limit": self.limit,
            "offset": self.offset,
            "includeDeleted": self.include_deleted,
        }
        params.update({k: v for k, v in extra.items() if v is not None})
        return params
