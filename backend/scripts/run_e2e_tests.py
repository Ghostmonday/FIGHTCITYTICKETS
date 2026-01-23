#!/usr/bin/env python3
"""
Run E2E Integration Tests for Fight City Tickets.com

This script runs comprehensive end-to-end integration tests that verify:
1. Stripe webhook integration works
2. Lob mail sending works
3. Hetzner droplet suspension works
4. All services communicate with the main Python FastAPI service

Usage:
    python run_e2e_tests.py
    python run_e2e_tests.py --verbose
    python run_e2e_tests.py --stripe-only
"""

import argparse
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import pytest  # noqa: E402


def main():
    """Run E2E integration tests."""
    parser = argparse.ArgumentParser(description="Run E2E integration tests")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--stripe-only", action="store_true", help="Test Stripe integration only"
    )
    parser.add_argument(
        "--lob-only", action="store_true", help="Test Lob integration only"
    )
    parser.add_argument(
        "--hetzner-only", action="store_true", help="Test Hetzner integration only"
    )
    parser.add_argument(
        "--full-flow", action="store_true", help="Test full integration flow only"
    )
    parser.add_argument(
        "--markers", "-m", help="Pytest markers to run (e.g., 'integration')"
    )

    args = parser.parse_args()

    # Build pytest arguments
    # Use relative path from backend directory
    import os
    test_file = os.path.join("tests", "test_e2e_integration.py")
    pytest_args = [
        test_file,
    ]

    if args.verbose:
        pytest_args.append("-v")

    if args.markers:
        pytest_args.extend(["-m", args.markers])
    else:
        pytest_args.extend(["-m", "integration"])

    # Filter by test class
    if args.stripe_only:
        pytest_args.append("::TestStripeWebhookIntegration")
    elif args.lob_only:
        pytest_args.append("::TestLobMailIntegration")
    elif args.hetzner_only:
        pytest_args.append("::TestHetznerDropletIntegration")
    elif args.full_flow:
        pytest_args.append("::TestFullIntegrationFlow")

    # Add color output
    pytest_args.append("--color=yes")

    # Run tests
    print("=" * 70)
    print("Running E2E Integration Tests")
    print("=" * 70)
    print("Arguments: {' '.join(pytest_args)}")
    print("=" * 70 + "\n")

    exit_code = pytest.main(pytest_args)

    if exit_code == 0:
        print("\n" + "=" * 70)
        print("[SUCCESS] ALL E2E INTEGRATION TESTS PASSED!")
        print("=" * 70)
        print("\nIf all four endpoints work, you've got a real product!")
    else:
        print("\n" + "=" * 70)
        print("[FAILED] SOME TESTS FAILED")
        print("=" * 70)
        print("\nCheck the output above for details.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

