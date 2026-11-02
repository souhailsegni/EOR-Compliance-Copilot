
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ollama import ollama_service


router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)


class ChatResponse(BaseModel):
    question: str
    answer: str
    model: str


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):

    try:
        answer = await ollama_service.generate_response(
            prompt=request.message,
            system_prompt=(
                "You are an AI assistant. "
                "Answer clearly and accurately. "
                "If you do not know something, say so."
            ),
        )

        return ChatResponse(
            question=request.message,
            answer=answer,
            model=ollama_service.model,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM service error: {str(exc)}",
        )
