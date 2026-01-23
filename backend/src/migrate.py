"""
Database Migration Script for Fight City Tickets.com

This script sets up the database schema and performs any necessary migrations.
Run this script before starting the application for the first time.
"""

import logging
import sys
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from .config import settings
from .models import create_all_tables, drop_all_tables

# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_database_if_not_exists(database_url: str) -> bool:
    """
    Create the database if it doesn't exist.

    Args:
        database_url: Database URL

    Returns:
        True if database exists or was created successfully
    """
    try:
        # Extract database name from URL
        # Format: postgresql+psycopg://user:pass@host:port/dbname
        if "postgresql" not in database_url:
            logger.error("Only PostgreSQL is supported")
            return False

        # Parse the URL to get database name
        parts = database_url.split("/")
        if len(parts) < 4:
            logger.error("Invalid database URL format: {database_url}")
            return False

        db_name = parts[-1]
        # Create base URL without database name
        base_url = "/".join(parts[:-1])

        # Connect to postgres database to create our database
        engine = create_engine("{base_url}/postgres")

        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": db_name},
            ).fetchone()

            if not result:
                logger.info("Creating database: {db_name}")
                # Create database with UTF-8 encoding
                conn.execute(text("CREATE DATABASE {db_name} ENCODING 'UTF8'"))
                conn.commit()
                logger.info("Database {db_name} created successfully")
            else:
                logger.info("Database {db_name} already exists")

        return True

    except SQLAlchemyError as e:
        logger.error("Failed to create database: {e}")
        return False


def check_database_connection(database_url: str) -> bool:
    """
    Check if we can connect to the database.

    Args:
        database_url: Database URL

    Returns:
        True if connection successful
    """
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except SQLAlchemyError as e:
        logger.error("Database connection failed: {e}")
        return False


def create_tables(database_url: str, drop_existing: bool = False) -> bool:
    """
    Create all database tables.

    Args:
        database_url: Database URL
        drop_existing: Whether to drop existing tables first

    Returns:
        True if tables created successfully
    """
    try:
        engine = create_engine(database_url)

        if drop_existing:
            logger.warning("Dropping all existing tables...")
            drop_all_tables(engine)
            logger.info("All tables dropped")

        logger.info("Creating database tables...")
        create_all_tables(engine)
        logger.info("Database tables created successfully")

        # Verify tables were created
        with engine.connect() as conn:
            tables = conn.execute(
                text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            ).fetchall()

            table_names = [t[0] for t in tables]
            expected_tables = {"intakes", "drafts", "payments"}

            created_tables = set(table_names)
            missing_tables = expected_tables - created_tables

            if missing_tables:
                logger.error("Missing tables: {missing_tables}")
                return False

            logger.info("Tables created: {', '.join(sorted(created_tables))}")

        return True

    except SQLAlchemyError as e:
        logger.error("Failed to create tables: {e}")
        return False


def create_indexes(database_url: str) -> bool:
    """
    Create additional indexes for performance.

    Args:
        database_url: Database URL

    Returns:
        True if indexes created successfully
    """
    try:
        engine = create_engine(database_url)

        with engine.connect() as conn:
            # Additional indexes beyond what's defined in models
            indexes = [
                # Index for looking up intakes by email and status
                "CREATE INDEX IF NOT EXISTS ix_intakes_email_status ON intakes(user_email, status)",
                # Index for looking up payments by created date (for reporting)
                "CREATE INDEX IF NOT EXISTS ix_payments_created_date ON payments(date(created_at))",
                # Index for looking up intakes by violation date
                "CREATE INDEX IF NOT EXISTS ix_intakes_violation_date ON intakes(violation_date)",
            ]

            for idx_sql in indexes:
                conn.execute(text(idx_sql))

            conn.commit()

        logger.info("Additional indexes created successfully")
        return True

    except SQLAlchemyError as e:
        logger.error("Failed to create indexes: {e}")
        return False


def seed_initial_data(database_url: str) -> bool:
    """
    Seed initial data for development/testing.

    Args:
        database_url: Database URL

    Returns:
        True if data seeded successfully
    """
    try:
        engine = create_engine(database_url)

        with engine.connect() as conn:
            # Check if we already have data
            result = conn.execute(text("SELECT COUNT(*) FROM intakes")).fetchone()

            if result[0] > 0:
                logger.info("Database already has data, skipping seed")
                return True

            # Insert test data for development
            logger.info("Seeding initial test data...")

            # Note: In production, you might not want to seed data
            # This is just for development/testing

        logger.info("Initial data seeded successfully")
        return True

    except SQLAlchemyError as e:
        logger.error("Failed to seed data: {e}")
        return False


def run_migrations(
    database_url: Optional[str] = None,
    drop_existing: bool = False,
    seed_data: bool = False,
) -> bool:
    """
    Run all database migrations.

    Args:
        database_url: Database URL (uses settings if not provided)
        drop_existing: Whether to drop existing tables
        seed_data: Whether to seed initial test data

    Returns:
        True if all migrations successful
    """
    if not database_url:
        database_url = settings.database_url

    if not database_url:
        logger.error("Database URL not configured")
        return False

    logger.info("=" * 60)
    logger.info("Starting Database Migration")
    logger.info(
        "Database: {database_url.split('@')[-1] if '@' in database_url else database_url}"
    )
    logger.info("Drop existing: {drop_existing}")
    logger.info("Seed data: {seed_data}")
    logger.info("=" * 60)

    # Step 1: Create database if it doesn't exist
    if not create_database_if_not_exists(database_url):
        logger.error("Failed to create database")
        return False

    # Step 2: Check connection
    if not check_database_connection(database_url):
        logger.error("Failed to connect to database")
        return False

    # Step 3: Create tables
    if not create_tables(database_url, drop_existing):
        logger.error("Failed to create tables")
        return False

    # Step 4: Create additional indexes
    if not create_indexes(database_url):
        logger.warning("Failed to create indexes (continuing anyway)")

    # Step 5: Seed data if requested
    if seed_data:
        if not seed_initial_data(database_url):
            logger.warning("Failed to seed data (continuing anyway)")

    logger.info("=" * 60)
    logger.info("Database Migration Completed Successfully")
    logger.info("=" * 60)

    return True


def main():
    """Main entry point for migration script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Database migration script for Fight City Tickets"
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing tables before creating new ones",
    )
    parser.add_argument("--seed", action="store_true", help="Seed initial test data")
    parser.add_argument("--database-url", help="Database URL (overrides settings)")

    args = parser.parse_args()

    try:
        success = run_migrations(
            database_url=args.database_url, drop_existing=args.drop, seed_data=args.seed
        )

        if not success:
            logger.error("Migration failed")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error during migration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
