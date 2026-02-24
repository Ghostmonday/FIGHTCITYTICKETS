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

def add_fleet_management():
    """Add fleet management tables and columns."""
    database_url = settings.database_url

    if not database_url:
        logger.error("Database URL not configured")
        return False

    try:
        engine = create_engine(database_url)

        with engine.connect() as conn:
            # 1. Create fleets table
            logger.info("Checking if 'fleets' table exists...")
            result = conn.execute(text("""
                SELECT to_regclass('public.fleets')
            """)).fetchone()

            if result and result[0]:
                logger.info("Table 'fleets' already exists.")
            else:
                logger.info("Creating 'fleets' table...")
                conn.execute(text("""
                    CREATE TABLE fleets (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) NOT NULL,
                        stripe_account_id VARCHAR(100),
                        stripe_account_status VARCHAR(50) DEFAULT 'pending',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
                    )
                """))

                # Add indexes
                conn.execute(text("CREATE INDEX ix_fleets_email ON fleets (email)"))
                conn.execute(text("CREATE INDEX ix_fleets_stripe_account_id ON fleets (stripe_account_id)"))
                logger.info("Table 'fleets' created successfully.")

            # 2. Add columns to intakes table
            logger.info("Checking 'intakes' table columns...")

            # Check fleet_id
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='intakes' AND column_name='fleet_id'
            """)).fetchone()

            if not result:
                logger.info("Adding 'fleet_id' column to 'intakes' table...")
                conn.execute(text("""
                    ALTER TABLE intakes
                    ADD COLUMN fleet_id INTEGER REFERENCES fleets(id)
                """))
                conn.execute(text("CREATE INDEX ix_intakes_fleet_id ON intakes (fleet_id)"))
            else:
                logger.info("Column 'fleet_id' already exists.")

            # Check is_fleet_managed
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='intakes' AND column_name='is_fleet_managed'
            """)).fetchone()

            if not result:
                logger.info("Adding 'is_fleet_managed' column to 'intakes' table...")
                conn.execute(text("""
                    ALTER TABLE intakes
                    ADD COLUMN is_fleet_managed BOOLEAN DEFAULT FALSE
                """))
            else:
                logger.info("Column 'is_fleet_managed' already exists.")

            conn.commit()
            logger.info("Migration completed successfully.")
            return True

    except Exception as e:
        logger.error(f"Failed to run migration: {e}")
        return False

if __name__ == "__main__":
    if add_fleet_management():
        sys.exit(0)
    else:
        sys.exit(1)
