# MCP Users API: Team and Manager Briefing

## Executive Summary

This project uses Model Context Protocol (MCP) as an integration layer between FastAPI and PostgreSQL. The architecture separates HTTP concerns from data-operation capabilities, making read/write behavior explicit through MCP resources and tools.

## Why This Matters

- Clear service contracts: reads and writes are represented as explicit MCP capabilities.
- Better change isolation: API routes are less coupled to SQL implementation details.
- Agent-readiness: the same capability surface can be reused by agentic clients.

## Current Architecture

Request path:

`Swagger -> FastAPI -> Controller -> MCP Client -> MCP DB Server -> PostgreSQL`

- Read via resources: `db://users`, `db://users/{user_id}`
- Write via tools: `create_user`, `update_user`, `delete_user`

See detailed flow in `request_flow.md` and workshop notebook in `mcp_demo.ipynb`.

## Business and Engineering Outcomes

- Faster onboarding: capability boundaries are easier to explain than mixed controller+SQL logic.
- Safer evolution: backend internals can change with lower API churn risk.
- Reuse potential: tools/resources can support future AI-assisted workflows.

## Risks and Tradeoffs

- Additional moving parts increase troubleshooting complexity.
- Process/session overhead can increase latency compared to direct DB calls.
- Requires disciplined logging, error mapping, and health checks.

## Recommended Next Steps

1. Add lightweight metrics for request count, error count, and latency by route/tool.
2. Add integration tests that cover API to MCP to DB flow.
3. Keep using deterministic MCP client calls for production paths and prompt-based flows for experimentation.
4. Run the demo notebook (`mcp_demo.ipynb`) in team onboarding sessions.
