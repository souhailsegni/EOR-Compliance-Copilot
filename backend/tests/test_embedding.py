
import asyncio

from app.services.embedding import embedding_service


async def main():
    text = "A worker must provide identity documents before onboarding."

    embedding = await embedding_service.generate_embedding(text)

    print("Embedding generated successfully!")
    print("Vector dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])


if __name__ == "__main__":
    asyncio.run(main())
