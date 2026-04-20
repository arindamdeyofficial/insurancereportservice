from typing import Annotated
from fastapi import APIRouter, Depends, Query
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services import clickhouse_client as ch
from app.services.cache import cache_get, cache_set

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _cached(key: str, fn, ttl: int = 120):
    hit = cache_get(key)
    if hit is not None:
        return hit
    result = fn()
    cache_set(key, result, ttl)
    return result


@router.get("/sentiment-trend")
def sentiment_trend(
    _: Annotated[User, Depends(get_current_user)],
    days: int = Query(30, ge=1, le=365),
):
    return _cached(f"analytics:sentiment_trend:{days}", lambda: ch.sentiment_trend(days))


@router.get("/incident-trend")
def incident_trend(
    _: Annotated[User, Depends(get_current_user)],
    days: int = Query(30, ge=1, le=365),
):
    return _cached(f"analytics:incident_trend:{days}", lambda: ch.incident_trend(days))


@router.get("/rival-leaderboard")
def rival_leaderboard(
    _: Annotated[User, Depends(get_current_user)],
    days: int = Query(30, ge=1, le=365),
):
    return _cached(f"analytics:rival_leaderboard:{days}", lambda: ch.rival_leaderboard(days))


@router.get("/source-activity")
def source_activity(
    _: Annotated[User, Depends(get_current_user)],
    days: int = Query(30, ge=1, le=365),
):
    return _cached(f"analytics:source_activity:{days}", lambda: ch.source_activity(days))
