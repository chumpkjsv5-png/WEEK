from dataclasses import asdict
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app import composition
from app.adapters.inbound.http.error_translation import translate_domain_errors
from app.application.use_cases.task_use_cases import (
    CompleteTask,
    CreateTask,
    DeleteTask,
    GetTask,
    ListTasks,
    UpdateTask,
)
from app.core.dependencies import get_current_user, require_role
from app.core.permissions import CAN_MANAGE, MEMBER
from app.domain.task import Actor, NewTask, TaskFilter
from app.models.user_data import User
from app.schemas.task_schema import (
    TaskCreate,
    TaskFilterParams,
    TaskListOut,
    TaskOut,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

CurrentUser = Annotated[User, Depends(get_current_user)]
ManagerUser = Annotated[User, Depends(require_role(*CAN_MANAGE))]

CreateUC = Annotated[CreateTask, Depends(composition.get_create_task)]
GetUC = Annotated[GetTask, Depends(composition.get_get_task)]
ListUC = Annotated[ListTasks, Depends(composition.get_list_tasks)]
UpdateUC = Annotated[UpdateTask, Depends(composition.get_update_task)]
CompleteUC = Annotated[CompleteTask, Depends(composition.get_complete_task)]
DeleteUC = Annotated[DeleteTask, Depends(composition.get_delete_task)]


def _plain(data: dict) -> dict:
    """Đổi Enum thành giá trị thường trước khi đưa vào lõi."""
    return {k: (v.value if isinstance(v, Enum) else v) for k, v in data.items()}


def _actor(user: User) -> Actor:
    return Actor(id=user.id, is_member=(user.role == MEMBER))


@router.post("/", response_model=TaskOut, status_code=201)
def create_task(task: TaskCreate, user: ManagerUser, uc: CreateUC):
    with translate_domain_errors():
        return uc.execute(NewTask(**_plain(task.model_dump())))


@router.get("/", response_model=TaskListOut)
def get_tasks(params: Annotated[TaskFilterParams, Query()], user: CurrentUser, uc: ListUC):
    with translate_domain_errors():
        page = uc.execute(TaskFilter(**_plain(params.model_dump())))
    return asdict(page)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, user: CurrentUser, uc: GetUC):
    with translate_domain_errors():
        return uc.execute(task_id)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task_update: TaskUpdate, user: CurrentUser, uc: UpdateUC):
    changes = _plain(task_update.model_dump(exclude_unset=True))
    with translate_domain_errors():
        return uc.execute(task_id, changes, _actor(user))


@router.patch("/{task_id}/complete", response_model=TaskOut)
def complete_task(task_id: int, user: CurrentUser, uc: CompleteUC):
    with translate_domain_errors():
        return uc.execute(task_id, _actor(user))


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, user: ManagerUser, uc: DeleteUC):
    with translate_domain_errors():
        uc.execute(task_id)