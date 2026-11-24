import asyncio

from app.services.embedding import embedding_service
from app.database.vector_store import vector_store


QUESTIONS = [
    "What documents are required before onboarding?",
    "How many days of annual leave does the employee receive?",
    "What is the statutory severance payment in Germany?",
]


async def main():
    for question in QUESTIONS:
        query_embedding = await embedding_service.generate_embedding(question)

        results = vector_store.search(
            query_embedding=query_embedding,
            top_k=3,
        )

        print("\n" + "=" * 70)
        print(f"QUESTION: {question}")

        for index, document in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][index]
            distance = results["distances"][0][index]

            print(
                f"\nPage: {metadata['page']} | "
                f"Distance: {distance:.4f}"
            )
            print(f"Text: {document[:180]}...")


if __name__ == "__main__":
    asyncio.run(main())