import logging
import sys
import os

# Add backend directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, text
from src.config import settings

# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def add_email_verified_column():
    """Add email_verified column to intakes table."""
    database_url = settings.database_url

    if not database_url:
        logger.error("Database URL not configured")
        return False

    try:
        engine = create_engine(database_url)

        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='intakes' AND column_name='email_verified'
            """)).fetchone()

            if result:
                logger.info("Column 'email_verified' already exists in 'intakes' table.")
                return True

            logger.info("Adding 'email_verified' column to 'intakes' table...")

            # Add column
            conn.execute(text("""
                ALTER TABLE intakes
                ADD COLUMN email_verified BOOLEAN DEFAULT FALSE
            """))

            # Add index is usually not needed for boolean unless high selectivity,
            # but we can do it if we query by unverified emails often.
            # Let's verify it worked
            conn.commit()

            logger.info("Column added successfully.")
            return True

    except Exception as e:
        logger.error(f"Failed to add column: {e}")
        return False

if __name__ == "__main__":
    if add_email_verified_column():
        sys.exit(0)
    else:
        sys.exit(1)
