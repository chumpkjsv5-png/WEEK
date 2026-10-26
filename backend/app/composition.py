from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session


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

from app.adapters.outbound.persistence.postgres_project_repository import (
    PostgresProjectRepository,
)
from app.application.ports.project_repository import ProjectRepository
from app.application.use_cases.project_use_cases import (
    CreateProject,
    DeleteProject,
    GetProject,
    ListProjects,
    UpdateProject,
)

from app.adapters.outbound.persistence.postgres_project_member_repository import (
    PostgresProjectMemberRepository,
)
from app.application.ports.project_member_repository import ProjectMemberRepository
from app.application.use_cases.project_member_use_cases import (
    AddMember,
    ListMembers,
    RemoveMember,
    SearchUsersToAdd,
)

# --- users và auth ---
from app.adapters.outbound.persistence.postgres_user_auth_repository import (  # noqa: E402
    PostgresUserAuthRepository,
)
from app.adapters.outbound.persistence.postgres_user_repository import (  # noqa: E402
    PostgresUserRepository,
)
from app.adapters.outbound.security.jwt_token_service import JwtTokenService  # noqa: E402
from app.adapters.outbound.security.pwdlib_password_verifier import (  # noqa: E402
    PwdlibPasswordVerifier,
)
from app.application.ports.security import PasswordVerifier, TokenService  # noqa: E402
from app.application.ports.user_auth_repository import UserAuthRepository  # noqa: E402
from app.application.ports.user_repository import UserRepository  # noqa: E402
from app.application.use_cases.auth_use_cases import AuthenticateToken, Login  # noqa: E402
from app.application.use_cases.user_use_cases import GetUser, SearchUsers  # noqa: E402


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

def get_task_repo(db: Annotated[Session, Depends(get_db)]) -> TaskRepository:
    return PostgresTaskRepository(db)

# TASKS
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

def get_project_repo(db: Annotated[Session, Depends(get_db)]) -> ProjectRepository:
    return PostgresProjectRepository(db)

# PROJECT

ProjectRepo = Annotated[ProjectRepository, Depends(get_project_repo)]


def get_list_projects(projects: ProjectRepo) -> ListProjects:
    return ListProjects(projects)


def get_get_project(projects: ProjectRepo) -> GetProject:
    return GetProject(projects)


def get_create_project(projects: ProjectRepo) -> CreateProject:
    return CreateProject(projects)


def get_update_project(projects: ProjectRepo) -> UpdateProject:
    return UpdateProject(projects)


def get_delete_project(projects: ProjectRepo) -> DeleteProject:
    return DeleteProject(projects)

# PROJECT_MEMBER

def get_project_member_repo(
    db: Annotated[Session, Depends(get_db)],
) -> ProjectMemberRepository:
    return PostgresProjectMemberRepository(db)


MemberRepo = Annotated[ProjectMemberRepository, Depends(get_project_member_repo)]


def get_list_members(repo: MemberRepo) -> ListMembers:
    return ListMembers(repo)


def get_search_users_to_add(repo: MemberRepo) -> SearchUsersToAdd:
    return SearchUsersToAdd(repo)


def get_add_member(repo: MemberRepo) -> AddMember:
    return AddMember(repo)


def get_remove_member(repo: MemberRepo) -> RemoveMember:
    return RemoveMember(repo)

#users
def get_user_repo(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    return PostgresUserRepository(db)


def get_user_auth_repo(db: Annotated[Session, Depends(get_db)]) -> UserAuthRepository:
    return PostgresUserAuthRepository(db)


def get_password_verifier() -> PasswordVerifier:
    return PwdlibPasswordVerifier()


def get_token_service() -> TokenService:
    return JwtTokenService()


UserRepo = Annotated[UserRepository, Depends(get_user_repo)]
AuthRepo = Annotated[UserAuthRepository, Depends(get_user_auth_repo)]
Verifier = Annotated[PasswordVerifier, Depends(get_password_verifier)]
Tokens = Annotated[TokenService, Depends(get_token_service)]


def get_search_users(users: UserRepo) -> SearchUsers:
    return SearchUsers(users)


def get_get_user(users: UserRepo) -> GetUser:
    return GetUser(users)


def get_login(users: AuthRepo, hasher: Verifier, tokens: Tokens) -> Login:
    return Login(users, hasher, tokens)


def get_authenticate_token(users: AuthRepo, tokens: Tokens) -> AuthenticateToken:
    return AuthenticateToken(users, tokens)
    
# ACTICLE

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