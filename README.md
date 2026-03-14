# MCP Users API Lab

This project exposes a local PostgreSQL-backed users service through:

- MCP server (tools and resources)
- FastAPI controller layer
- Swagger UI for interactive read/write requests

## Architecture

HTTP request -> FastAPI controller -> MCP client service -> MCP DB server -> PostgreSQL

- Reads use MCP resources:
  - `db://users`
  - `db://users/{user_id}`
- Writes use MCP tools:
  - `create_user`
  - `update_user`
  - `delete_user`

## Project Files

- `src/db_server.py`: MCP server with DB resources/tools
- `src/services/mcp_client.py`: service bridge from HTTP layer to MCP
- `src/controllers/user_controller.py`: API controller routes
- `src/api_server.py`: FastAPI app and Swagger/OpenAPI
- `docker-compose.yml`: local PostgreSQL setup
- `db/init/001_create_users.sql`: users table schema init

## Prerequisites

- Docker Desktop running
- Python 3.12+
- `uv` installed

## Setup

1. Install dependencies:

```bash
uv pip install -r requirements.txt
```

2. Start PostgreSQL:

```bash
docker compose up -d
```

3. Verify DB is up:

```bash
docker compose ps
```

## Run the API (Swagger)

Start FastAPI server:

```bash
uv run uvicorn src.api_server:app --reload
```

Open Swagger UI:

- http://127.0.0.1:8000/docs

Open OpenAPI JSON:

- http://127.0.0.1:8000/openapi.json

## Available Endpoints

- `GET /health`
- `GET /users`
- `GET /users/{user_id}`
- `POST /users`
- `PUT /users/{user_id}`
- `DELETE /users/{user_id}`

## Example Requests (curl)

Create user:

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Nadav","email":"nadav@example.com"}'
```

List users:

```bash
curl http://127.0.0.1:8000/users
```

Get user:

```bash
curl http://127.0.0.1:8000/users/1
```

Update user:

```bash
curl -X PUT http://127.0.0.1:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Nadav B","email":"nadavb@example.com"}'
```

Delete user:

```bash
curl -X DELETE http://127.0.0.1:8000/users/1
```

## Local DB Config

Defaults are in `.env`:

- `POSTGRES_HOST=127.0.0.1`
- `POSTGRES_PORT=5432`
- `POSTGRES_DB=mcp_lab`
- `POSTGRES_USER=mcp_user`
- `POSTGRES_PASSWORD=mcp_password`

## Stop Services

Stop API: Ctrl+C in terminal.

Stop DB:

```bash
docker compose down
```

## Notes

- The HTTP API does not access PostgreSQL directly.
- Controllers always go through MCP client service.
- If MCP server is unavailable, endpoints return a structured fail payload.