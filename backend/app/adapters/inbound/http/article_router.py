from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app import composition
from app.adapters.inbound.http.error_translation import translate_domain_errors
from app.application.use_cases.article_use_cases import (
    DEFAULT_ARTICLE_LIMIT,
    MAX_ARTICLE_LIMIT,
    CreateArticle,
    CreateArticleCommand,
    GetArticle,
    SearchArticles,
)
from app.adapters.inbound.http.dependencies import get_current_user
from app.domain.article import ContentBlock
from app.models.user_data import User
from app.schemas.article_schema import (
    ArticleBrief,
    ArticleBriefList,
    ArticleCreate,
    ArticleDetail,
)

router = APIRouter(prefix="/articles", tags=["articles"])

CurrentUser = Annotated[User, Depends(get_current_user)]
CreateUC = Annotated[CreateArticle, Depends(composition.get_create_article)]
GetUC = Annotated[GetArticle, Depends(composition.get_get_article)]
SearchUC = Annotated[SearchArticles, Depends(composition.get_search_articles)]


def _to_domain_blocks(blocks: list) -> list[ContentBlock]:
    result = []
    for b in blocks:
        d = b.model_dump()
        result.append(ContentBlock(id=d.pop("id"), type=d.pop("type"), data=d))
    return result


def _to_dicts(blocks: list[ContentBlock]) -> list[dict]:
    return [{"id": b.id, "type": b.type, **b.data} for b in blocks]


@router.post("", response_model=ArticleBrief, status_code=201)
def create_article(data: ArticleCreate, user: CurrentUser, uc: CreateUC):
    cmd = CreateArticleCommand(
        owner_id=user.id,  # lấy từ người đăng nhập, client không tự khai được
        title=data.title,
        tags=data.tags,
        blocks=_to_domain_blocks(data.blocks),
    )
    with translate_domain_errors():
        return uc.execute(cmd)


@router.get("", response_model=ArticleBriefList)
def search_articles(
    user: CurrentUser,
    uc: SearchUC,
    q: Optional[str] = Query(default=None, max_length=100),
    tag: Optional[str] = Query(default=None, max_length=50),
    limit: int = Query(default=DEFAULT_ARTICLE_LIMIT, ge=1, le=MAX_ARTICLE_LIMIT),
    offset: int = Query(default=0, ge=0),
):
    with translate_domain_errors():
        return uc.execute(q=q, tag=tag, limit=limit, offset=offset)


@router.get("/{article_id}", response_model=ArticleDetail)
def get_article(article_id: int, user: CurrentUser, uc: GetUC):
    with translate_domain_errors():
        result = uc.execute(article_id)
    brief = ArticleBrief.model_validate(result.article)
    return ArticleDetail(**brief.model_dump(), blocks=_to_dicts(result.blocks))