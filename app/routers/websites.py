from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user, require_role
from app.models.website import Website
from app.models.user import User
from app.schemas.website import WebsiteCreate, WebsiteOut

router = APIRouter(prefix="/websites", tags=["websites"])


@router.get("", response_model=list[WebsiteOut])
def list_websites(
    _: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    active_only: bool = False,
):
    q = db.query(Website)
    if active_only:
        q = q.filter(Website.is_active == True)
    return q.order_by(Website.language, Website.name).all()


@router.post("", response_model=WebsiteOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin", "analyst"))])
def create_website(body: WebsiteCreate, db: Annotated[Session, Depends(get_db)]):
    site = Website(**body.model_dump())
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.patch("/{site_id}/toggle", response_model=WebsiteOut,
              dependencies=[Depends(require_role("admin", "analyst"))])
def toggle_website(site_id: int, db: Annotated[Session, Depends(get_db)]):
    site = db.get(Website, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Website not found")
    site.is_active = not site.is_active
    db.commit()
    db.refresh(site)
    return site


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_role("admin"))])
def delete_website(site_id: int, db: Annotated[Session, Depends(get_db)]):
    site = db.get(Website, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Website not found")
    db.delete(site)
    db.commit()
