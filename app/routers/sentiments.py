from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.sentiment import Sentiment
from app.models.user import User
from app.schemas.sentiment import SentimentOut
from app.services.cache import cache_get, cache_set

router = APIRouter(prefix="/sentiments", tags=["sentiments"])


@router.get("", response_model=list[SentimentOut])
def list_sentiments(
    _: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    label: str | None = Query(None),
):
    cache_key = f"sentiments:{skip}:{limit}:{label}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    q = db.query(Sentiment).options(joinedload(Sentiment.article))
    if label:
        q = q.filter(Sentiment.label == label)
    rows = q.order_by(Sentiment.created_at.desc()).offset(skip).limit(limit).all()
    result = [SentimentOut.model_validate(r).model_dump(mode="json") for r in rows]
    cache_set(cache_key, result, ttl=300)
    return rows
