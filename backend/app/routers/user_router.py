import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user_data import User
from app.schemas.user_schema import UserBrief, UserBriefList
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=UserBriefList)
def search_users(
    db: DbSession,
    user: CurrentUser,
    search: Optional[str] = Query(default=None, max_length=100),
    limit: int = Query(default=user_service.DEFAULT_USER_LIMIT, ge=1, le=user_service.MAX_USER_LIMIT),
):
    return user_service.search_users(db, search=search, limit=limit)


@router.get("/{user_id}", response_model=UserBrief)
def get_user(user_id: uuid.UUID, db: DbSession, user: CurrentUser):
    return user_service.get_user(db, user_id)