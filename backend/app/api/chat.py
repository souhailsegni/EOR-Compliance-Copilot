
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.schemas.answer import AnswerResponse
from app.services.answer_generation import answer_generation_service


router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=5000)


@router.post("/", response_model=AnswerResponse)
async def chat(request: ChatRequest) -> AnswerResponse:

    try:
        result = await answer_generation_service.generate_answer(
            question=request.message
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Answer generation service error.",
        ) from exc
