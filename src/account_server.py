from mcp.server.fastmcp import FastMCP
from typing import Any
import logging
mcp = FastMCP("account_server")

@mcp.tool(name="get_account_info", description="Get account information for a given user ID.")
async def get_account_info(user_id: str) -> dict[str, Any]:
    # Simulate fetching account info (replace with real logic)
    return {
        "user_id": user_id,
        "name": "John Doe",
        "email": "john.doe@example.com"
    }

@mcp.tool(name="hello_test_tool", description="A simple tool that returns a greeting message.")
async def hello_tool() -> str:
    return "Hello, world!"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("mcp.server.fastmcp").setLevel(logging.DEBUG)
    logging.info("Starting MCP server for account_server.py")
    mcp.run(transport="stdio")