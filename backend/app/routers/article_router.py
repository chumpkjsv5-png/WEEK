from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from pymongo.collection import Collection
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user_data import User
from app.mongo import get_content_collection
from app.schemas.article_schema import (
    ArticleBrief,
    ArticleBriefList,
    ArticleCreate,
    ArticleDetail,
)
from app.services import article_service

router = APIRouter(prefix="/articles", tags=["articles"])

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
ContentCol = Annotated[Collection, Depends(get_content_collection)]


@router.post("", response_model=ArticleBrief, status_code=201)
def create_article(data: ArticleCreate, db: DbSession, content: ContentCol, user: CurrentUser):
    # owner lấy từ người đăng nhập, client không tự khai được
    return article_service.create_article(db, content, user, data)


@router.get("", response_model=ArticleBriefList)
def search_articles(
    db: DbSession,
    user: CurrentUser,
    q: Optional[str] = Query(default=None, max_length=100),
    tag: Optional[str] = Query(default=None, max_length=50),
    limit: int = Query(default=article_service.DEFAULT_ARTICLE_LIMIT, ge=1, le=article_service.MAX_ARTICLE_LIMIT),
    offset: int = Query(default=0, ge=0),
):
    return article_service.search_articles(db, q=q, tag=tag, limit=limit, offset=offset)


@router.get("/{article_id}", response_model=ArticleDetail)
def get_article(article_id: int, db: DbSession, content: ContentCol, user: CurrentUser):
    result = article_service.get_article(db, content, article_id)
    brief = ArticleBrief.model_validate(result["article"])
    return ArticleDetail(**brief.model_dump(), blocks=result["blocks"])