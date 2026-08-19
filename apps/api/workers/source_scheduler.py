from datetime import UTC, datetime, timedelta

from app.source.source_model import Source

DAILY_INTERVAL = timedelta(days=1)
WEEKLY_INTERVAL = timedelta(days=7)


def should_check_source(
    source: Source,
    now: datetime | None = None,
) -> bool:
    """
    Decide whether a source should be checked now.

    Rules:
        quality >= 5  -> daily
        quality < 5   -> weekly

    A source that has never been checked is always checked.
    """

    now = now or datetime.now(UTC)

    # First check: always run.
    if source.last_checked is None:
        return True

    quality = float(source.quality_score or 0.0)

    if quality >= 5:
        interval = DAILY_INTERVAL
    else:
        interval = WEEKLY_INTERVAL

    return now - source.last_checked >= interval
