from apscheduler.schedulers.background import BackgroundScheduler
from app.config import settings

_scheduler: BackgroundScheduler | None = None


def start_scheduler():
    global _scheduler
    from app.services.worker import ingest_news

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        ingest_news,
        "interval",
        minutes=settings.SCRAPE_INTERVAL_MINUTES,
        id="ingest_news",
        replace_existing=True,
    )
    _scheduler.start()


def stop_scheduler():
    if _scheduler:
        _scheduler.shutdown(wait=False)
