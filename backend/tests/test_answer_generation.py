
import asyncio

from app.services.answer_generation import answer_generation_service


TEST_CASES = [
    {
        "question": "What documents are required before onboarding?",
        "expected_confidence": "high",
        "expected_escalation": False,
        "expected_pages": [1],
    },
    {
        "question": "How many days of annual leave does the employee receive?",
        "expected_confidence": "medium",
        "expected_escalation": True,
        "expected_pages": [2],
    },
    {
        "question": "What is the statutory severance payment in Germany?",
        "expected_confidence": "low",
        "expected_escalation": True,
        "expected_pages": [],
    },
]


async def main():

    passed = 0
    failed = 0

    for test_number, test_case in enumerate(TEST_CASES, start=1):

        question = test_case["question"]

        result = await answer_generation_service.generate_answer(
            question
        )

        actual_pages = sorted({
            item["page"] for item in result["evidence"]
        })

        checks = {
            "confidence": (
                result["confidence"]
                == test_case["expected_confidence"]
            ),
            "escalation": (
                result["escalation_required"]
                == test_case["expected_escalation"]
            ),
            "evidence_pages": (
                actual_pages == test_case["expected_pages"]
            ),
        }

        test_passed = all(checks.values())

        if test_passed:
            passed += 1
        else:
            failed += 1

        print("\n" + "=" * 70)
        print(f"TEST {test_number}: {question}")
        print("-" * 70)

        print(f"ANSWER: {result['answer']}")
        print(f"CONFIDENCE: {result['confidence']}")
        print(f"ESCALATION: {result['escalation_required']}")
        print(f"EVIDENCE PAGES: {actual_pages}")

        print("\nCHECKS:")

        for check_name, check_result in checks.items():
            status = "PASS" if check_result else "FAIL"
            print(f"{check_name}: {status}")

        print(f"\nRESULT: {'PASS' if test_passed else 'FAIL'}")

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total tests: {len(TEST_CASES)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed:
        raise AssertionError(
            f"{failed} evaluation test(s) failed."
        )


if __name__ == "__main__":
    asyncio.run(main())
