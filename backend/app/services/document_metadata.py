import re
from datetime import datetime
from pathlib import Path

from app.rag.document_loader import load_pdf
from backend.app.schemas.document import DocumentMetadata


def _extract_field(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)

    if not match:
        return None

    return match.group(1).strip()


def _extract_effective_date(text: str):
    value = _extract_field(
        r"Effective date:\s*(.+)",
        text,
    )

    if not value:
        return None

    for date_format in ("%d %B %Y", "%d %b %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            continue

    return None


def extract_document_metadata(file_path: str) -> DocumentMetadata:
    path = Path(file_path)
    pages = load_pdf(path)

    # Use the first two pages for metadata extraction.
    # The title and metadata fields are usually near the beginning.
    first_pages_text = "\n".join(
        page["text"] for page in pages[:2]
    )

    first_nonempty_line = next(
        (
            line.strip()
            for line in first_pages_text.splitlines()
            if line.strip()
        ),
        None,
    )

    return DocumentMetadata(
        filename=path.name,
        document_title=first_nonempty_line,
        source_document_id=_extract_field(
            r"Document ID:\s*([^|\n]+)",
            first_pages_text,
        ),
        version=_extract_field(
            r"Version:\s*([^|\n]+)",
            first_pages_text,
        ),
        effective_date=_extract_effective_date(first_pages_text),
        # These are not reliably inferred yet; leave them for user review.
        country=None,
        document_type=None,
    )