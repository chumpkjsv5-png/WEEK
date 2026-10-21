from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.adapters.outbound.persistence.mongo_article_content_repository import (
    MongoArticleContentRepository,
)
from app.adapters.outbound.persistence.postgres_article_repository import (
    PostgresArticleRepository,
)
from app.application.ports.article_content_repository import ArticleContentRepository
from app.application.ports.article_metadata_repository import ArticleMetadataRepository
from app.application.use_cases.article_use_cases import (
    CreateArticle,
    GetArticle,
    SearchArticles,
)
from app.database import get_db
from app.mongo import get_content_collection


def get_article_meta_repo(
    db: Annotated[Session, Depends(get_db)],
) -> ArticleMetadataRepository:
    return PostgresArticleRepository(db)


def get_article_content_repo() -> ArticleContentRepository:
    return MongoArticleContentRepository(get_content_collection())


ArticleMetaRepo = Annotated[ArticleMetadataRepository, Depends(get_article_meta_repo)]
ArticleContentRepo = Annotated[ArticleContentRepository, Depends(get_article_content_repo)]


def get_create_article(meta: ArticleMetaRepo, content: ArticleContentRepo) -> CreateArticle:
    return CreateArticle(meta, content)


def get_get_article(meta: ArticleMetaRepo, content: ArticleContentRepo) -> GetArticle:
    return GetArticle(meta, content)


def get_search_articles(meta: ArticleMetaRepo) -> SearchArticles:
    return SearchArticles(meta)