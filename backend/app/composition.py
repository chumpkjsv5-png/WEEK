from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.adapters.outbound.persistence.mongo_article_content_repository import (
    MongoArticleContentRepository,
)
from app.adapters.outbound.persistence.postgres_article_repository import (
    PostgresArticleRepository,
)
from app.adapters.outbound.persistence.postgres_task_repository import (
    PostgresTaskRepository,
)
from app.application.ports.task_repository import TaskRepository
from app.application.use_cases.task_use_cases import (
    CompleteTask,
    CreateTask,
    DeleteTask,
    GetTask,
    ListTasks,
    UpdateTask,
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

def get_task_repo(db: Annotated[Session, Depends(get_db)]) -> TaskRepository:
    return PostgresTaskRepository(db)


TaskRepo = Annotated[TaskRepository, Depends(get_task_repo)]


def get_create_task(tasks: TaskRepo) -> CreateTask:
    return CreateTask(tasks)


def get_get_task(tasks: TaskRepo) -> GetTask:
    return GetTask(tasks)


def get_list_tasks(tasks: TaskRepo) -> ListTasks:
    return ListTasks(tasks)


def get_update_task(tasks: TaskRepo) -> UpdateTask:
    return UpdateTask(tasks)


def get_complete_task(tasks: TaskRepo) -> CompleteTask:
    return CompleteTask(tasks)


def get_delete_task(tasks: TaskRepo) -> DeleteTask:
    return DeleteTask(tasks)


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