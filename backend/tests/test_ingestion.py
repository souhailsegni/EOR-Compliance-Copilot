
import asyncio

from app.services.ingestion import ingestion_service
from app.database.vector_store import vector_store


async def main():
    result = await ingestion_service.ingest_pdf(
        "test_docs/eor_test_document.pdf"
    )

    print("INGESTION RESULT")
    print(result)

    print("\nCHROMADB")
    print("Stored chunks:", vector_store.collection.count())


if __name__ == "__main__":
    asyncio.run(main())
