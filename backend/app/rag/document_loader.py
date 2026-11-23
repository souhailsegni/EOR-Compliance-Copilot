from pathlib import Path

from pypdf import PdfReader


def load_pdf(file_path: str | Path) -> list[dict]:
    """
    Extract text from a PDF, returning one record per page.

    Each record contains:
    - text: extracted page text
    - source: PDF filename
    - page: 1-based page number
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"PDF file not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    reader = PdfReader(str(path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()

        if not text:
            continue

        pages.append(
            {
                "text": text,
                "source": path.name,
                "page": page_number,
            }
        )

    if not pages:
        raise ValueError(
            f"No extractable text found in PDF: {path.name}. "
            "The file may be scanned or image-only."
        )

    return pages