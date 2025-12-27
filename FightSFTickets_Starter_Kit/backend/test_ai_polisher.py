#!/usr/bin/env python3
"""
Test AI Polisher with Profanity Filtering and UPL Compliance
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.statement import refine_statement, DeepSeekService

async def test_profanity_filtering():
    """Test that profanity is removed from statements."""
    print("=" * 60)
    print("Testing AI Polisher - Profanity Filtering")
    print("=" * 60)
    print()

    # Test cases with profanity
    test_cases = [
        {
            "name": "Heavy Profanity",
            "statement": "This is fucking bullshit! I got a ticket but the meter was broken as hell. What the shit is this?",
            "citation": "912345678"
        },
        {
            "name": "Mixed Profanity",
            "statement": "Damn, I parked there for like 5 minutes and got a ticket. The meter didn't work and I'm pissed off about it.",
            "citation": "912345679"
        },
        {
            "name": "Casual Profanity",
            "statement": "I think this is crap. The parking meter was broken and I couldn't pay. This is really bad.",
            "citation": "912345680"
        },
        {
            "name": "Clean Statement",
            "statement": "I parked at the meter but it was not functioning properly. I attempted to pay but the machine would not accept my payment.",
            "citation": "912345681"
        }
    ]

    _service = DeepSeekService()

    for i, test_case in enumerate(test_cases, 1):
        print("Test {i}: {test_case['name']}")
        print("Original: {test_case['statement']}")
        print()

        try:
            result = await refine_statement(
                original_statement=test_case['statement'],
                citation_number=test_case['citation'],
                max_length=1000
            )

            print("Status: {result.status}")
            print("Method: {result.method_used}")
            print("Refined ({len(result.refined_statement)} chars):")
            print(result.refined_statement[:300] + "..." if len(result.refined_statement) > 300 else result.refined_statement)

            # Check for profanity in refined statement
            profanity_words = ['fuck', 'shit', 'damn', 'hell', 'ass', 'bitch', 'crap', 'piss', 'bullshit']
            found_profanity = [word for word in profanity_words if word.lower() in result.refined_statement.lower()]

            if found_profanity:
                print("⚠️  WARNING: Profanity still present: {found_profanity}")
            else:
                print("✅ No profanity detected in refined statement")

            print()
            print("-" * 60)
            print()

        except Exception as e:
            print("ERROR: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("=" * 60)
    print("Profanity Filtering Test Complete")
    print("=" * 60)

async def test_upl_compliance():
    """Test that AI doesn't provide legal advice."""
    print()
    print("=" * 60)
    print("Testing AI Polisher - UPL Compliance")
    print("=" * 60)
    print()

    # Test case that might trigger legal advice
    test_statement = "I got a ticket but I don't know what to do. Should I include photos? What evidence should I submit?"

    print("Test Statement (trying to get legal advice):")
    print(f'"{test_statement}"')
    print()

    try:
        result = await refine_statement(
            original_statement=test_statement,
            citation_number="912345682",
            max_length=1000
        )

        print("Refined Statement:")
        print(result.refined_statement)
        print()

        # Check for legal advice indicators
        legal_advice_indicators = [
            'should include', 'should submit', 'should provide',
            'recommend', 'suggest', 'advise', 'you must',
            'you need to', 'you should', 'legal advice',
            'evidence you should', 'you ought to'
        ]

        found_advice = [indicator for indicator in legal_advice_indicators
                       if indicator.lower() in result.refined_statement.lower()]

        if found_advice:
            print("WARNING: Possible legal advice detected: {found_advice}")
        else:
            print("SUCCESS: No legal advice detected - UPL compliant")

        print()
        print("=" * 60)
        print("UPL Compliance Test Complete")
        print("=" * 60)

    except Exception as e:
        print("❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests."""
    await test_profanity_filtering()
    await test_upl_compliance()

    print()
    print("SUCCESS: All tests completed!")
    print()
    print("Next: Deploy to production")

if __name__ == "__main__":
    asyncio.run(main())

