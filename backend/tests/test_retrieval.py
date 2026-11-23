
import asyncio
from app.services.retrieval import retrieval_service


QUESTIONS = [
    "What documents are required before onboarding?",
    "How many days of annual leave does the employee receive?",
    "What is the statutory severance payment in Germany?",
]


async def main():
    for question in QUESTIONS:
        results = await retrieval_service.retrieve(
            question=question,
            top_k=3,
        )

        print("\n" + "=" * 70)
        print(f"QUESTION: {question}")
        print(f"RETRIEVED CHUNKS: {len(results)}")

        for index, item in enumerate(results, start=1):
            print(f"\nResult {index}")
            print(f"Source: {item['source']}")
            print(f"Page: {item['page']}")
            print(f"Distance: {item['distance']:.4f}")
            print(f"Text: {item['text'][:250]}...")


if __name__ == "__main__":
    asyncio.run(main())
