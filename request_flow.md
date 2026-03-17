# Request Flow (Swagger -> DB -> Response)

This diagram shows how a request moves from Swagger through the API and MCP layers to PostgreSQL, then back to the client.

```mermaid
sequenceDiagram
    autonumber
    participant U as User (Swagger UI)
    participant API as FastAPI (api_server)
    participant C as Controller (user_controller)
    participant S as MCP Client (services/mcp_client)
    participant M as MCP DB Server (db_server)
    participant DB as PostgreSQL

    U->>API: HTTP request (/users...)
    API->>C: Route handler
    C->>S: Call service method
    S->>M: MCP resource/tool request
    M->>DB: SQL query/command
    DB-->>M: rows/status
    M-->>S: structured result
    S-->>C: normalized payload
    C-->>API: response object
    API-->>U: JSON response in Swagger
```

## Notes

- Reads are done via MCP resources (`db://users`, `db://users/{user_id}`).
- Writes are done via MCP tools (`create_user`, `update_user`, `delete_user`).
- FastAPI never talks directly to PostgreSQL; it always goes through the MCP client/server boundary.
