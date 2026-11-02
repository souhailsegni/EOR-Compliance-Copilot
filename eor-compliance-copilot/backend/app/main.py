from fastapi import FastAPI

from app.core.config import settings
from app.api.health import router as health_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered EOR Compliance Assistant",
)

app.include_router(health_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to EOR Compliance Copilot",
        "version": settings.APP_VERSION,
    }