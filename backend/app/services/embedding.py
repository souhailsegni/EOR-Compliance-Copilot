
import httpx

from app.core.config import settings


class EmbeddingService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = "nomic-embed-text"

    async def generate_embedding(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Cannot generate an embedding for empty text.")

        url = f"{self.base_url}/api/embed"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                json={
                    "model": self.model,
                    "input": text,
                },
            )

            response.raise_for_status()
            data = response.json()

        embeddings = data.get("embeddings")

        if not embeddings or not embeddings[0]:
            raise ValueError("Ollama returned an empty embedding.")

        return embeddings[0]


embedding_service = EmbeddingService()
