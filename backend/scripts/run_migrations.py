#!/usr/bin/env python3
"""
Migration script for FightSFTickets backend.

This script handles database migrations in different environments:
1. Test environment (SQLite) - for local development without Docker
2. Development environment (PostgreSQL via Docker)
3. Production environment (PostgreSQL)

Usage:
    python scripts/run_migrations.py [--env test|dev|prod] [--action create|upgrade|downgrade|history]

Examples:
    # Create initial migration in test environment
    python scripts/run_migrations.py --env test --action create --message "Initial schema"

    # Upgrade to latest migration in test environment
    python scripts/run_migrations.py --env test --action upgrade

    # Show migration history
    python scripts/run_migrations.py --env test --action history
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def load_environment(env: str) -> None:
    """Load environment variables for the specified environment."""
    env_file = backend_dir / f".env.{env}"

    if env_file.exists():
        print(f"Loading environment from: {env_file}")
        # Load environment variables from file
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print(f"Warning: Environment file {env_file} not found")
        print("Using existing environment variables")


def run_alembic_command(args: list) -> int:
    """Run an alembic command and return the exit code."""
    cmd = [sys.executable, "-m", "alembic"] + args
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, cwd=backend_dir, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Errors:\n{result.stderr}", file=sys.stderr)
        return result.returncode
    except FileNotFoundError:
        print("Error: alembic not found. Make sure it's installed.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error running alembic: {e}", file=sys.stderr)
        return 1


def create_migration(message: str) -> int:
    """Create a new migration."""
    if not message:
        print("Error: Migration message is required for create action", file=sys.stderr)
        return 1

    return run_alembic_command(["revision", "--autogenerate", "-m", message])


def upgrade_migration(revision: str = "head") -> int:
    """Upgrade to a specific revision (default: head)."""
    return run_alembic_command(["upgrade", revision])


def downgrade_migration(revision: str) -> int:
    """Downgrade to a specific revision."""
    return run_alembic_command(["downgrade", revision])


def show_history() -> int:
    """Show migration history."""
    return run_alembic_command(["history"])


def show_current() -> int:
    """Show current migration."""
    return run_alembic_command(["current"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Database migration tool")
    parser.add_argument(
        "--env",
        choices=["test", "dev", "prod"],
        default="test",
        help="Environment to run migrations in (default: test)",
    )
    parser.add_argument(
        "--action",
        choices=["create", "upgrade", "downgrade", "history", "current"],
        default="upgrade",
        help="Migration action to perform (default: upgrade)",
    )
    parser.add_argument(
        "--message", help="Migration message (required for create action)"
    )
    parser.add_argument(
        "--revision",
        default="head",
        help="Revision to upgrade/downgrade to (default: head for upgrade)",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.action == "create" and not args.message:
        parser.error("--message is required for create action")

    # Load environment
    load_environment(args.env)

    # Perform action
    if args.action == "create":
        return create_migration(args.message)
    elif args.action == "upgrade":
        return upgrade_migration(args.revision)
    elif args.action == "downgrade":
        return downgrade_migration(args.revision)
    elif args.action == "history":
        return show_history()
    elif args.action == "current":
        return show_current()

    return 0


if __name__ == "__main__":
    sys.exit(main())
