from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import require_role
from app.models.user import User
from app.schemas.auth import UserOut
from app.services.worker import ingest_news

router = APIRouter(prefix="/admin", tags=["admin"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ROLES = {"admin", "analyst", "viewer"}


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "viewer"


@router.get("/users", response_model=list[UserOut], dependencies=[Depends(require_role("admin"))])
def list_users(db: Annotated[Session, Depends(get_db)]):
    return db.query(User).all()


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin"))])
def create_user(body: CreateUserRequest, db: Annotated[Session, Depends(get_db)]):
    if body.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of {ROLES}")
    if db.query(User).filter_by(email=body.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=body.email,
        password_hash=pwd_context.hash(body.password),
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/scrape", dependencies=[Depends(require_role("admin", "analyst"))])
def trigger_scrape(background_tasks: BackgroundTasks):
    background_tasks.add_task(ingest_news)
    return {"message": "Scrape job enqueued"}
