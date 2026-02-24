"""
Task scheduler for background jobs.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .models import ScrapedPage
from .services.address_validator import CITY_URL_MAPPING, get_address_validator
from .services.database import get_db_service

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: AsyncIOScheduler | None = None


async def run_address_verification_job():
    """
    Run address verification for all configured cities.

    This job runs daily and checks if the appeal address on the city's website
    matches our stored address. If not, it updates the stored address.
    """
    logger.info("Starting scheduled address verification job")

    validator = get_address_validator()

    success_count = 0
    mismatch_count = 0
    error_count = 0

    # Iterate over all cities configured for verification
    for city_id in CITY_URL_MAPPING:
        try:
            logger.info("Verifying address for %s", city_id)
            result = await validator.validate_address(city_id)

            if result.is_valid:
                logger.debug("Address verified for %s", city_id)
                success_count += 1
            elif result.was_updated:
                logger.warning(
                    "Address mismatch for %s - updated successfully",
                    city_id
                )
                mismatch_count += 1
            else:
                logger.error(
                    "Address verification failed for %s: %s",
                    city_id,
                    result.error_message,
                )
                error_count += 1

        except Exception:
            logger.exception("Error running address verification for %s", city_id)
            error_count += 1

    logger.info(
        "Address verification job completed. Success: %d, Updated: %d, Errors: %d",
        success_count,
        mismatch_count,
        error_count,
    )


async def purge_expired_scraped_pages() -> None:
    """
    Delete ScrapedPage rows whose 90-day retention window has expired.

    Runs weekly (Sunday 03:00 UTC) to keep the audit table bounded in size.
    """
    logger.info("Starting ScrapedPage expiry purge")
    try:
        db = get_db_service()
        with db.get_session() as session:
            deleted = (
                session.query(ScrapedPage)
                .filter(ScrapedPage.expires_at < datetime.now(timezone.utc))
                .delete(synchronize_session=False)
            )
            session.commit()
        logger.info("ScrapedPage purge complete — deleted %d rows", deleted)
    except Exception:
        logger.exception("Error during ScrapedPage expiry purge")


def start_scheduler() -> AsyncIOScheduler:
    """
    Start the background scheduler.

    Returns:
        The started scheduler instance.
    """
    global _scheduler

    if _scheduler is not None and _scheduler.running:
        return _scheduler

    logger.info("Initializing background scheduler")
    _scheduler = AsyncIOScheduler()

    # Add address verification job - Run daily at 4:00 AM UTC
    _scheduler.add_job(
        run_address_verification_job,
        trigger=CronTrigger(hour=4, minute=0, timezone=timezone.utc),
        id="address_verification",
        name="Daily Address Verification",
        replace_existing=True,
        coalesce=True,
        misfire_grace_time=3600  # Allow 1 hour grace time if missed
    )

    # Add ScrapedPage expiry purge - runs every Sunday at 03:00 AM UTC
    _scheduler.add_job(
        purge_expired_scraped_pages,
        trigger=CronTrigger(day_of_week="sun", hour=3, minute=0, timezone=timezone.utc),
        id="scraped_page_purge",
        name="Weekly ScrapedPage Expiry Purge",
        replace_existing=True,
        coalesce=True,
        misfire_grace_time=3600,
    )

    _scheduler.start()
    logger.info("Background scheduler started")

    return _scheduler


def shutdown_scheduler():
    """Shutdown the scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        logger.info("Shutting down background scheduler")
        _scheduler.shutdown()
        _scheduler = None
