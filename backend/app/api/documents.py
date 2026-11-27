import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.ingestion import ingestion_service


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict:
    filename = file.filename or ""

    if Path(filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="The PDF must be 10 MB or smaller.",
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file does not appear to be a valid PDF.",
        )

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".pdf",
            delete=False,
        ) as temporary_file:
            temporary_file.write(content)
            temporary_path = temporary_file.name

        result = await ingestion_service.ingest_pdf(temporary_path)

        # Return the user's original filename, not the temporary one.
        result["filename"] = Path(filename).name
        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed.",
        ) from exc

    finally:
        if temporary_path:
            Path(temporary_path).unlink(missing_ok=True)

        await file.close()