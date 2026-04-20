from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.incident import Incident
from app.models.user import User
from app.schemas.incident import IncidentOut
from app.services.cache import cache_get, cache_set

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentOut])
def list_incidents(
    _: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    severity: str | None = Query(None),
):
    cache_key = f"incidents:{skip}:{limit}:{severity}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    q = db.query(Incident).options(joinedload(Incident.article))
    if severity:
        q = q.filter(Incident.severity == severity)
    rows = q.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()
    result = [IncidentOut.model_validate(r).model_dump(mode="json") for r in rows]
    cache_set(cache_key, result, ttl=300)
    return rows
