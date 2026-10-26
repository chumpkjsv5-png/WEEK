import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app import composition
from app.adapters.inbound.http.dependencies import get_current_user
from app.adapters.inbound.http.error_translation import translate_domain_errors
from app.application.use_cases.user_use_cases import (
    DEFAULT_USER_LIMIT,
    MAX_USER_LIMIT,
    GetUser,
    SearchUsers,
)
from app.domain.auth import AuthUser
from app.schemas.user_schema import UserBrief, UserBriefList

router = APIRouter(prefix="/users", tags=["users"])

CurrentUser = Annotated[AuthUser, Depends(get_current_user)]
SearchUC = Annotated[SearchUsers, Depends(composition.get_search_users)]
GetUC = Annotated[GetUser, Depends(composition.get_get_user)]


@router.get("", response_model=UserBriefList)
def search_users(
    user: CurrentUser,
    uc: SearchUC,
    search: Optional[str] = Query(default=None, max_length=100),
    limit: int = Query(default=DEFAULT_USER_LIMIT, ge=1, le=MAX_USER_LIMIT),
):
    with translate_domain_errors():
        return uc.execute(search=search, limit=limit)


@router.get("/{user_id}", response_model=UserBrief)
def get_user(user_id: uuid.UUID, user: CurrentUser, uc: GetUC):
    with translate_domain_errors():
        return uc.execute(user_id)
