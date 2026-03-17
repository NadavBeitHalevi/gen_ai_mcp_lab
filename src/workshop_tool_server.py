from __future__ import annotations
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tool_only_demo")


@mcp.tool(name="create_user", description="Create user mutation demo")
async def create_user(name: str, email: str) -> dict[str, Any]:
    return {
        "success": True,
        "message": "Tool mutation demo",
        "data": {"user": {"name": name, "email": email}},
    }
