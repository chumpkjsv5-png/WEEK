class ArticleNotFound(Exception):
    pass


class ContentMissing(Exception):
    pass


class StoreUnavailable(Exception):
    pass

# project     
class ProjectForbidden(Exception):
    pass


class ProjectOwnerChangeForbidden(Exception):
    pass


class OwnerNotFound(Exception):
    pass

# Tasks
class TaskNotFound(Exception):
    pass


class ProjectNotFound(Exception):
    pass


class AssigneeNotFound(Exception):
    pass


class AssigneeNotProjectMember(Exception):
    pass


class TaskNotAssignedToYou(Exception):
    pass


class TaskStatusOnly(Exception):
    pass

# Project_member
class ProjectMemberForbidden(Exception):
    pass


class UserNotFound(Exception):
    pass


class MemberAlreadyExists(Exception):
    pass


class MemberNotFound(Exception):
    pass


class CannotRemoveOwner(Exception):
    pass


class MemberHasOpenTasks(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class AccountDisabled(Exception):
    pass


class NotAuthenticated(Exception):
    pass


class InvalidSession(Exception):
    pass
