from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.rival_ad import RivalAd
from app.models.user import User
from app.schemas.rival_ad import RivalAdOut
from app.services.cache import cache_get, cache_set

router = APIRouter(prefix="/rival-ads", tags=["rival-ads"])


@router.get("", response_model=list[RivalAdOut])
def list_rival_ads(
    _: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    competitor: str | None = Query(None),
):
    cache_key = f"rival_ads:{skip}:{limit}:{competitor}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    q = db.query(RivalAd).options(joinedload(RivalAd.article))
    if competitor:
        q = q.filter(RivalAd.competitor_name.ilike(f"%{competitor}%"))
    rows = q.order_by(RivalAd.created_at.desc()).offset(skip).limit(limit).all()
    result = [RivalAdOut.model_validate(r).model_dump(mode="json") for r in rows]
    cache_set(cache_key, result, ttl=300)
    return rows
