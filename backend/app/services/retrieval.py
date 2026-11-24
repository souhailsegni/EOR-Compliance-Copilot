
from app.services.embedding import embedding_service
from app.database.vector_store import vector_store


class RetrievalService:
    def __init__(self, max_distance: float = 0.50):
        self.max_distance = max_distance

    async def retrieve(
        self,
        question: str,
        top_k: int = 3,
    ) -> list[dict]:

        query_embedding = await embedding_service.generate_embedding(question)

        results = vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        retrieved_chunks = []

        for index, document in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][index]
            distance = results["distances"][0][index]

            # Exclude chunks that are not sufficiently relevant.
            if distance > self.max_distance:
                continue

            retrieved_chunks.append({
                "text": document,
                "source": metadata["source"],
                "page": metadata["page"],
                "document_id": metadata["document_id"],
                "distance": distance,
            })

        return retrieved_chunks


retrieval_service = RetrievalService()
