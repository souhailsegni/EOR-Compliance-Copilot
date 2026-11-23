
import hashlib
from pathlib import Path

from app.rag.document_loader import load_pdf
from app.rag.chunking import chunk_pages
from app.services.embedding import embedding_service
from app.database.vector_store import vector_store


class IngestionService:
    async def ingest_pdf(self, file_path: str) -> dict:
        path = Path(file_path)

        # 1. Extract PDF text
        pages = load_pdf(path)

        # 2. Split extracted text into chunks
        chunks = chunk_pages(
            pages,
            chunk_size=1000,
            chunk_overlap=200,
        )

        document_id = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        # 3. Generate embeddings
        for index, chunk in enumerate(chunks):
            chunk["id"] = f"{document_id}_{index}"
            chunk["document_id"] = document_id
            chunk["embedding"] = (
                await embedding_service.generate_embedding(
                    chunk["text"]
                )
            )

        # 4. Store chunks and embeddings
        vector_store.add_chunks(chunks)

        return {
            "document_id": document_id,
            "filename": path.name,
            "pages_processed": len(pages),
            "chunks_created": len(chunks),
            "status": "success",
        }


ingestion_service = IngestionService()
