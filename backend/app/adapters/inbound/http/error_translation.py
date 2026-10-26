from contextlib import contextmanager

from app.core.exceptions import (
    BadRequestError,
    ConflictError,
    ContentMissingError,
    ForbiddenError,
    NotFoundError,
    StoreUnavailableError,
    UnauthorizedError,
)
from app.domain.errors import (
    AccountDisabled,
    ArticleNotFound,
    AssigneeNotFound,
    AssigneeNotProjectMember,
    CannotRemoveOwner,
    ContentMissing,
    InvalidCredentials,
    InvalidSession,
    MemberAlreadyExists,
    MemberHasOpenTasks,
    MemberNotFound,
    NotAuthenticated,
    OwnerNotFound,
    ProjectForbidden,
    ProjectMemberForbidden,
    ProjectNotFound,
    ProjectOwnerChangeForbidden,
    StoreUnavailable,
    TaskNotAssignedToYou,
    TaskNotFound,
    TaskStatusOnly,
    UserNotFound,
)

# (lỗi domain, lỗi HTTP, mã code; None = dùng mã mặc định của lớp HTTP)
_TRANSLATIONS = [
    # articles
    (ArticleNotFound, NotFoundError, "ARTICLE_NOT_FOUND"),
    (ContentMissing, ContentMissingError, None),
    (StoreUnavailable, StoreUnavailableError, None),
    # tasks
    (TaskNotFound, NotFoundError, "TASK_NOT_FOUND"),
    (ProjectNotFound, NotFoundError, "PROJECT_NOT_FOUND"),
    (AssigneeNotFound, NotFoundError, "ASSIGNEE_NOT_FOUND"),
    (AssigneeNotProjectMember, BadRequestError, "ASSIGNEE_NOT_PROJECT_MEMBER"),
    (TaskNotAssignedToYou, ForbiddenError, "TASK_NOT_ASSIGNED_TO_YOU"),
    (TaskStatusOnly, ForbiddenError, "TASK_STATUS_ONLY"),
    # projects
    (ProjectForbidden, ForbiddenError, "PROJECT_FORBIDDEN"),
    (ProjectOwnerChangeForbidden, ForbiddenError, "PROJECT_OWNER_CHANGE_FORBIDDEN"),
    (OwnerNotFound, BadRequestError, "OWNER_NOT_FOUND"),
    # project members
    (ProjectMemberForbidden, ForbiddenError, "PROJECT_MEMBER_FORBIDDEN"),
    (UserNotFound, NotFoundError, "USER_NOT_FOUND"),
    (MemberAlreadyExists, ConflictError, "MEMBER_ALREADY_EXISTS"),
    (MemberNotFound, NotFoundError, "MEMBER_NOT_FOUND"),
    (CannotRemoveOwner, ConflictError, "CANNOT_REMOVE_OWNER"),
    (MemberHasOpenTasks, ConflictError, "MEMBER_HAS_OPEN_TASKS"),
    # auth
    (InvalidCredentials, UnauthorizedError, "INVALID_CREDENTIALS"),
    (AccountDisabled, ForbiddenError, "ACCOUNT_DISABLED"),
    (NotAuthenticated, UnauthorizedError, "UNAUTHORIZED"),
    (InvalidSession, UnauthorizedError, "UNAUTHORIZED"),
]


@contextmanager
def translate_domain_errors():
    try:
        yield
    except Exception as e:
        for domain_exc, http_exc, code in _TRANSLATIONS:
            if isinstance(e, domain_exc):
                raise http_exc(str(e), code=code) from e
        raise