from app.rag.document_loader import load_pdf
from app.rag.chunking import chunk_pages

pages = load_pdf("test_docs/eor_test_document.pdf")

chunks = chunk_pages(
    pages,
    chunk_size=500,
    chunk_overlap=100,
)

print(f"Extracted pages: {len(pages)}")
print(f"Generated chunks: {len(chunks)}")

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {index} ---")
    print(f"Source: {chunk['source']}")
    print(f"Page: {chunk['page']}")
    print(f"Text: {chunk['text'][:150]}...")