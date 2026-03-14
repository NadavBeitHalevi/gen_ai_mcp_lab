import argparse
import asyncio

from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio, MCPServerStdioParams

load_dotenv()


def build_prompt(args: argparse.Namespace) -> str:
    if args.command == "create":
        return (
            "Use the create_user tool with the provided values and return the tool output only. "
            f"name={args.name}, email={args.email}."
        )

    if args.command == "update":
        return (
            "Use the update_user tool with the provided values and return the tool output only. "
            f"user_id={args.user_id}, name={args.name}, email={args.email}."
        )

    if args.command == "delete":
        return (
            "Use the delete_user tool and return the tool output only. "
            f"user_id={args.user_id}."
        )

    if args.command == "get":
        return (
            "Read the db://users/{user_id} resource and return the exact resource output only. "
            f"user_id={args.user_id}."
        )

    return "Read the db://users resource and return the exact resource output only."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CLI client for the db_server MCP server")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_cmd = subparsers.add_parser("create", help="Create a user")
    create_cmd.add_argument("--name", required=True, help="User name")
    create_cmd.add_argument("--email", required=True, help="User email")

    update_cmd = subparsers.add_parser("update", help="Update a user")
    update_cmd.add_argument("--user-id", type=int, required=True, help="User ID")
    update_cmd.add_argument("--name", required=True, help="Updated user name")
    update_cmd.add_argument("--email", required=True, help="Updated user email")

    delete_cmd = subparsers.add_parser("delete", help="Delete a user")
    delete_cmd.add_argument("--user-id", type=int, required=True, help="User ID")

    get_cmd = subparsers.add_parser("get", help="Get a single user")
    get_cmd.add_argument("--user-id", type=int, required=True, help="User ID")

    subparsers.add_parser("list", help="List all users")

    return parser.parse_args()


async def run_cli(args: argparse.Namespace) -> None:
    server_params = MCPServerStdioParams(command="uv", args=["run", "src/db_server.py"])

    async with MCPServerStdio(params=server_params, client_session_timeout_seconds=60) as server:
        agent = Agent(
            name="DB Client Agent",
            instructions=(
                "You are a strict MCP DB client. "
                "Always call the relevant db_server tool/resource and return only the final JSON output."
            ),
            model="gpt-4o-mini",
            mcp_servers=[server],
        )

        prompt = build_prompt(args)
        with trace("Running DB Client Agent"):
            result = await Runner.run(agent, prompt)
            print(result.final_output)


def main() -> None:
    args = parse_args()
    asyncio.run(run_cli(args))


if __name__ == "__main__":
    main()