from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.mcp_client import mcp_db_client

router = APIRouter(prefix="/users", tags=["Users"])


class CreateUserRequest(BaseModel):
    name: str
    email: str


class UpdateUserRequest(BaseModel):
    name: str
    email: str


def _raise_http_if_failed(payload: dict[str, Any], not_found_message: str | None = None) -> None:
    if payload.get("success") is True:
        return

    # Map MCP-domain failures to HTTP semantics while preserving original payload.
    message = str(payload.get("message", "Operation failed"))
    if not_found_message and not_found_message in message:
        raise HTTPException(status_code=404, detail=payload)
    if "must be an integer" in message:
        raise HTTPException(status_code=422, detail=payload)
    raise HTTPException(status_code=400, detail=payload)


@router.get("/get_users")
async def list_users() -> dict[str, Any]:
    payload = await mcp_db_client.list_users()
    _raise_http_if_failed(payload)
    return payload


@router.get("/{user_id}")
async def get_user(user_id: int) -> dict[str, Any]:
    payload = await mcp_db_client.get_user(user_id)
    _raise_http_if_failed(payload, not_found_message="not found")
    return payload


@router.post("/create_user")
async def create_user(request: CreateUserRequest) -> dict[str, Any]:
    payload = await mcp_db_client.create_user(name=request.name, email=str(request.email))
    _raise_http_if_failed(payload)
    return payload


@router.put("/update_user/{user_id}")
async def update_user(user_id: int, request: UpdateUserRequest) -> dict[str, Any]:
    payload = await mcp_db_client.update_user(
        user_id=user_id,
        name=request.name,
        email=str(request.email),
    )
    _raise_http_if_failed(payload, not_found_message="not found")
    return payload


@router.delete("/delete_user/{user_id}")
async def delete_user(user_id: int) -> dict[str, Any]:
    payload = await mcp_db_client.delete_user(user_id=user_id)
    _raise_http_if_failed(payload, not_found_message="not found")
    return payload