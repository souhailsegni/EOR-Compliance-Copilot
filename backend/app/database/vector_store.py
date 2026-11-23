
import chromadb

from pathlib import Path


class VectorStore:
    def __init__(self, persist_directory: str = "data/chroma"):
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name="eor_documents",
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: list[dict]) -> None:
        if not chunks:
            return

        ids = []
        documents = []
        metadatas = []
        embeddings = []

        for chunk in chunks:
            ids.append(chunk["id"])
            documents.append(chunk["text"])
            metadatas.append({
                "source": chunk["source"],
                "page": chunk["page"],
                "document_id": chunk["document_id"],
            })
            embeddings.append(chunk["embedding"])

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> dict:
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )


vector_store = VectorStore()
