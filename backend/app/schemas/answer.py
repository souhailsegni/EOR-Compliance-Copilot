
from typing import Literal

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    source: str
    page: int
    document_id: str
    section: str | None = None


class EvidenceAssessment(BaseModel):
    sufficiency: Literal["full", "partial", "none"]
    reason: str
    relevant_evidence_indices: list[int] = Field(default_factory=list)


class AnswerResponse(BaseModel):
    answer: str

    evidence: list[EvidenceItem] = Field(
        default_factory=list
    )

    confidence: Literal["high", "medium", "low"]
    confidence_reason: str

    escalation_required: bool
    escalation_reason: str | None = None

    follow_up_questions: list[str] = Field(
        default_factory=list
    )
