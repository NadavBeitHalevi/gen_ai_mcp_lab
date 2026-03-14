from __future__ import annotations

import json
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from pydantic import AnyUrl, TypeAdapter


class MCPDBClient:
    def __init__(self) -> None:
        self._server_params = StdioServerParameters(command="uv", args=["run", "src/db_server.py"])

    async def _with_session(self) -> ClientSession:
        raise RuntimeError("Use within async context manager")

    @staticmethod
    def _to_any_url(uri: str) -> AnyUrl:
        return TypeAdapter(AnyUrl).validate_python(uri)

    @staticmethod
    def _parse_json_text(text: str) -> dict[str, Any]:
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
            return {"success": False, "message": "Unexpected non-object response", "data": parsed}
        except json.JSONDecodeError:
            return {"success": False, "message": "Invalid JSON response from MCP", "data": text}

    async def _call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            # Keep each request isolated by opening a short-lived stdio MCP session.
            async with stdio_client(self._server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(name, arguments)

            # FastMCP returns structuredContent for dict outputs; this is the preferred path.
            if isinstance(result.structuredContent, dict):
                return result.structuredContent

            # Fallback for servers that only return text payloads.
            if result.content and hasattr(result.content[0], "text"):
                return self._parse_json_text(result.content[0].text)

            return {"success": False, "message": "Empty tool response", "data": None}
        except Exception as exc:
            return {"success": False, "message": f"MCP tool call failed: {exc}", "data": None}

    async def _read_resource(self, uri: str) -> dict[str, Any]:
        try:
            # Read flows use MCP resources exactly as requested by the architecture.
            async with stdio_client(self._server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.read_resource(self._to_any_url(uri))

            if not result.contents:
                return {"success": False, "message": "Empty resource response", "data": None}

            first_content = result.contents[0]
            if hasattr(first_content, "text"):
                return self._parse_json_text(first_content.text)

            return {"success": False, "message": "Unsupported resource content type", "data": None}
        except Exception as exc:
            return {"success": False, "message": f"MCP resource read failed: {exc}", "data": None}

    async def list_users(self) -> dict[str, Any]:
        return await self._read_resource("db://users")

    async def get_user(self, user_id: int) -> dict[str, Any]:
        return await self._read_resource(f"db://users/{user_id}")

    async def create_user(self, name: str, email: str) -> dict[str, Any]:
        return await self._call_tool("create_user", {"name": name, "email": email})

    async def update_user(self, user_id: int, name: str, email: str) -> dict[str, Any]:
        return await self._call_tool(
            "update_user",
            {"user_id": user_id, "name": name, "email": email},
        )

    async def delete_user(self, user_id: int) -> dict[str, Any]:
        return await self._call_tool("delete_user", {"user_id": user_id})


mcp_db_client = MCPDBClient()