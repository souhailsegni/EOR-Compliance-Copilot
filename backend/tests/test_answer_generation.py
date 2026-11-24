import asyncio

from app.services.answer_generation import answer_generation_service


QUESTIONS = [
    "What documents are required before onboarding?",
    "How many days of annual leave does the employee receive?",
    "What is the statutory severance payment in Germany?",
]


async def main():
    for question in QUESTIONS:
        result = await answer_generation_service.generate_answer(question)

        print("\n" + "=" * 70)
        print(f"QUESTION: {question}")
        print(f"\nANSWER:\n{result['answer']}")
        print(f"\nEVIDENCE: {result['evidence']}")
        print(f"CONFIDENCE: {result['confidence']}")
        print(f"CONFIDENCE REASON: {result['confidence_reason']}")
        print(f"ESCALATION REQUIRED: {result['escalation_required']}")
        print(f"ESCALATION REASON: {result['escalation_reason']}")
        print(f"FOLLOW-UP QUESTIONS: {result['follow_up_questions']}")


if __name__ == "__main__":
    asyncio.run(main())