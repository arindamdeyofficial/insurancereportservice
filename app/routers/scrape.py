from typing import Annotated
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import require_role
from app.models.website import Website

router = APIRouter(prefix="/scrape", tags=["scrape"])


class ScrapeRequest(BaseModel):
    website_ids: list[int] = []


@router.post("", dependencies=[Depends(require_role("admin", "analyst"))])
def trigger_scrape(
    body: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
):
    if body.website_ids:
        sites = db.query(Website).filter(
            Website.id.in_(body.website_ids), Website.is_active == True
        ).all()
    else:
        sites = db.query(Website).filter(Website.is_active == True).all()

    sources = [{"name": s.name, "rss": s.rss_url, "url": s.url, "scrape": not bool(s.rss_url)} for s in sites if s.rss_url or s.url]
    background_tasks.add_task(_run_scrape, sources)
    return {"message": f"Scrape triggered for {len(sources)} website(s)"}


def _run_scrape(sources: list[dict]):
    from app.services.worker import ingest_news_sources
    ingest_news_sources(sources)
