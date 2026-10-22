from contextlib import contextmanager

from app.core.exceptions import (
    BadRequestError,
    ContentMissingError,
    ForbiddenError,
    NotFoundError,
    StoreUnavailableError,
    ConflictError,
)
from app.domain.errors import (
    ArticleNotFound,
    AssigneeNotFound,
    AssigneeNotProjectMember,   
    ContentMissing,
    ProjectNotFound,
    StoreUnavailable,
    TaskNotAssignedToYou,
    TaskNotFound,
    TaskStatusOnly,
    OwnerNotFound,
    ProjectForbidden,
    ProjectOwnerChangeForbidden,
    CannotRemoveOwner,
    MemberAlreadyExists,
    MemberHasOpenTasks,
    MemberNotFound,
    ProjectMemberForbidden,
    UserNotFound,
)

# (lỗi domain, lỗi HTTP, mã code; None = dùng mã mặc định của lớp HTTP)
_TRANSLATIONS = [
    (ArticleNotFound, NotFoundError, "ARTICLE_NOT_FOUND"),
    (TaskNotFound, NotFoundError, "TASK_NOT_FOUND"),
    (ProjectNotFound, NotFoundError, "PROJECT_NOT_FOUND"),
    (AssigneeNotFound, NotFoundError, "ASSIGNEE_NOT_FOUND"),
    (AssigneeNotProjectMember, BadRequestError, "ASSIGNEE_NOT_PROJECT_MEMBER"),
    (TaskNotAssignedToYou, ForbiddenError, "TASK_NOT_ASSIGNED_TO_YOU"),
    (TaskStatusOnly, ForbiddenError, "TASK_STATUS_ONLY"),
    (ProjectForbidden, ForbiddenError, "PROJECT_FORBIDDEN"),
    (ProjectOwnerChangeForbidden, ForbiddenError, "PROJECT_OWNER_CHANGE_FORBIDDEN"),
    (OwnerNotFound, BadRequestError, "OWNER_NOT_FOUND"),
    # project_member
    (ProjectMemberForbidden, ForbiddenError, "PROJECT_MEMBER_FORBIDDEN"),
    (UserNotFound, NotFoundError, "USER_NOT_FOUND"),
    (MemberAlreadyExists, ConflictError, "MEMBER_ALREADY_EXISTS"),
    (MemberNotFound, NotFoundError, "MEMBER_NOT_FOUND"),
    (CannotRemoveOwner, ConflictError, "CANNOT_REMOVE_OWNER"),
    (MemberHasOpenTasks, ConflictError, "MEMBER_HAS_OPEN_TASKS"),
    (ContentMissing, ContentMissingError, None),
    (StoreUnavailable, StoreUnavailableError, None),
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