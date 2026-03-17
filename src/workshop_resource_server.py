from __future__ import annotations
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("resource_only_demo")


@mcp.resource("demo://users")
async def users_resource() -> dict[str, Any]:
    return {
        "success": True,
        "message": "Read-only resource demo",
        "data": {"users": [{"id": 1, "name": "Alice", "email": "alice@example.com"}]},
    }
