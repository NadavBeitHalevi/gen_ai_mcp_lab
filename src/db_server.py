from typing import Any
import logging
import os

import asyncpg
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("db_server")


def _db_config() -> dict[str, Any]:
    return {
        "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "database": os.getenv("POSTGRES_DB", "mcp_lab"),
        "user": os.getenv("POSTGRES_USER", "mcp_user"),
        "password": os.getenv("POSTGRES_PASSWORD", "mcp_password"),
    }


async def _connect() -> asyncpg.Connection:
    return await asyncpg.connect(**_db_config())


async def ensure_schema() -> None:
    conn = await _connect()
    try:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
    finally:
        await conn.close()


def _ok(message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"success": True, "message": message, "data": data}


def _fail(message: str) -> dict[str, Any]:
    return {"success": False, "message": message, "data": None}


@mcp.resource("db://users")
async def users_resource() -> dict[str, Any]:
    conn = await _connect()
    try:
        rows = await conn.fetch(
            "SELECT id, name, email, created_at FROM users ORDER BY id;"
        )
        users = [dict(row) for row in rows]
        return _ok("Fetched users", {"users": users, "count": len(users)})
    except Exception as exc:
        return _fail(f"Failed to fetch users: {exc}")
    finally:
        await conn.close()


@mcp.resource("db://users/{user_id}")
async def user_resource(user_id: str) -> dict[str, Any]:
    conn = await _connect()
    try:
        row = await conn.fetchrow(
            "SELECT id, name, email, created_at FROM users WHERE id = $1;",
            int(user_id),
        )
        if row is None:
            return _fail(f"User {user_id} not found")
        return _ok("Fetched user", {"user": dict(row)})
    except ValueError:
        return _fail("user_id must be an integer")
    except Exception as exc:
        return _fail(f"Failed to fetch user: {exc}")
    finally:
        await conn.close()


@mcp.tool(name="create_user", description="Create a user record in PostgreSQL.")
async def create_user(name: str, email: str) -> dict[str, Any]:
    conn = await _connect()
    try:
        row = await conn.fetchrow(
            """
            INSERT INTO users(name, email)
            VALUES($1, $2)
            RETURNING id, name, email, created_at;
            """,
            name,
            email,
        )
        return _ok("User created", {"user": dict(row) if row else None})
    except asyncpg.UniqueViolationError:
        return _fail("Email already exists")
    except Exception as exc:
        return _fail(f"Failed to create user: {exc}")
    finally:
        await conn.close()


@mcp.tool(name="update_user", description="Update an existing user record.")
async def update_user(user_id: int, name: str, email: str) -> dict[str, Any]:
    conn = await _connect()
    try:
        row = await conn.fetchrow(
            """
            UPDATE users
            SET name = $2, email = $3
            WHERE id = $1
            RETURNING id, name, email, created_at;
            """,
            user_id,
            name,
            email,
        )
        if row is None:
            return _fail(f"User {user_id} not found")
        return _ok("User updated", {"user": dict(row)})
    except asyncpg.UniqueViolationError:
        return _fail("Email already exists")
    except Exception as exc:
        return _fail(f"Failed to update user: {exc}")
    finally:
        await conn.close()


@mcp.tool(name="delete_user", description="Delete a user record by ID.")
async def delete_user(user_id: int) -> dict[str, Any]:
    conn = await _connect()
    try:
        result = await conn.execute("DELETE FROM users WHERE id = $1;", user_id)
        deleted_count = int(result.split(" ")[-1])
        if deleted_count == 0:
            return _fail(f"User {user_id} not found")
        return _ok("User deleted", {"deleted_count": deleted_count})
    except Exception as exc:
        return _fail(f"Failed to delete user: {exc}")
    finally:
        await conn.close()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    logging.getLogger("mcp.server.fastmcp").setLevel(logging.DEBUG)
    logging.info("Ensuring PostgreSQL schema for db_server")
    asyncio.run(ensure_schema())
    logging.info("Starting MCP server for db_server.py")
    mcp.run(transport="stdio")