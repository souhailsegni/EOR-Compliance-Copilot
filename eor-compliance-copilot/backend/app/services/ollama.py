import httpx

from app.core.config import settings


class OllamaService:

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def check_connection(self) -> dict:
        url = f"{self.base_url}/api/tags"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                response.raise_for_status()

                data = response.json()

                models = [
                    model["name"]
                    for model in data.get("models", [])
                ]

                available = self.model in models

                return {
                    "connected": True,
                    "model": self.model,
                    "model_available": available,
                    "available_models": models,
                }

        except httpx.HTTPError as exc:
            return {
                "connected": False,
                "model": self.model,
                "model_available": False,
                "error": str(exc),
            }


ollama_service = OllamaService()