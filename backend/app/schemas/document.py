from datetime import date

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    filename: str
    document_title: str | None = None
    source_document_id: str | None = None
    version: str | None = None
    effective_date: date | None = None
    country: str | None = None
    document_type: str | None = None