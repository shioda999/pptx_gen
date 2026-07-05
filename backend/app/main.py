from fastapi import FastAPI

from app.api.routes import router as api_router


app = FastAPI(
    title="PPT Agent Core API",
    version="0.1.0",
    description="Self-hosted PowerPoint generation core for Dify, Hermes Agent, and future MCP wrappers.",
)
app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
