from fastapi import FastAPI

from src.controllers.user_controller import router as users_router

app = FastAPI(
    title="MCP Users API",
    description="Swagger API that routes user read/write operations through an MCP controller-client chain.",
    version="1.0.0",
)


@app.get("/health", tags=["Health"]) # type: ignore
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(users_router)