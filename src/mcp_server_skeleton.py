from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp_demo_skeleton")


def _ok(message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"success": True, "message": message, "data": data}


@mcp.resource("demo://health")
async def health_resource() -> dict[str, Any]:
    return _ok("Skeleton server is healthy", {"service": "mcp_demo_skeleton"})




@mcp.tool(name="echo_user", description="Echo back validated user info for demo purposes.")
async def echo_user(name: str, email: str) -> dict[str, Any]:
    return _ok("Echo tool executed", {"user": {"name": name, "email": email}})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting demo MCP skeleton")
    mcp.run(transport="stdio")
