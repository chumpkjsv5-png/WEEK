class ArticleNotFound(Exception):
    pass


class ContentMissing(Exception):
    pass


class StoreUnavailable(Exception):
    pass
    

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