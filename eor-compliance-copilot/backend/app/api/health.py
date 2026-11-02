from fastapi import APIRouter

from app.services.ollama import ollama_service


router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "EOR Compliance Copilot",
    }


@router.get("/health/llm")
async def llm_health_check():
    return await ollama_service.check_connection()