
import asyncio

from app.services.answer_generation import answer_generation_service


async def main():

    question = "What documents are required before onboarding?"

    result = await answer_generation_service.generate_answer(
        question
    )

    print("\nQUESTION:")
    print(question)

    print("\nGENERATED ANSWER:")
    print(result["answer"])

    print("\nEVIDENCE:")
    for item in result["evidence"]:
        print(item)

    print("\nESCALATION REQUIRED:")
    print(result["escalation_required"])

    print("\nREASON:")
    print(result["reason"])


if __name__ == "__main__":
    asyncio.run(main())
