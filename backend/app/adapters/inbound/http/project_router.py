from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app import composition
from app.adapters.inbound.http.error_translation import translate_domain_errors
from app.application.use_cases.project_use_cases import (
    CreateProject,
    DeleteProject,
    GetProject,
    ListProjects,
    UpdateProject,
)
from app.core.dependencies import get_current_user, require_role
from app.core.permissions import ADMIN, CAN_MANAGE, MANAGER
from app.domain.project import ProjectActor, ProjectFilter
from app.models.user_data import User
from app.schemas.project_schema import (
    ProjectCreate,
    ProjectFilterParams,
    ProjectListOut,
    ProjectOut,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])

CurrentUser = Annotated[User, Depends(get_current_user)]
ManagerUser = Annotated[User, Depends(require_role(*CAN_MANAGE))]

ListUC = Annotated[ListProjects, Depends(composition.get_list_projects)]
GetUC = Annotated[GetProject, Depends(composition.get_get_project)]
CreateUC = Annotated[CreateProject, Depends(composition.get_create_project)]
UpdateUC = Annotated[UpdateProject, Depends(composition.get_update_project)]
DeleteUC = Annotated[DeleteProject, Depends(composition.get_delete_project)]


def _actor(user: User) -> ProjectActor:
    return ProjectActor(
        id=user.id,
        is_admin=(user.role == ADMIN),
        is_manager=(user.role == MANAGER),
    )


@router.get("", response_model=ProjectListOut)
def get_projects(
    params: Annotated[ProjectFilterParams, Query()], user: CurrentUser, uc: ListUC
):
    with translate_domain_errors():
        page = uc.execute(ProjectFilter(**params.model_dump()))
    return asdict(page)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, user: CurrentUser, uc: GetUC):
    with translate_domain_errors():
        return uc.execute(project_id)


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, user: ManagerUser, uc: CreateUC):
    with translate_domain_errors():
        return uc.execute(payload.name, payload.description, _actor(user))


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int, payload: ProjectUpdate, user: ManagerUser, uc: UpdateUC
):
    changes = payload.model_dump(exclude_unset=True)
    with translate_domain_errors():
        return uc.execute(project_id, changes, _actor(user))


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, user: ManagerUser, uc: DeleteUC):
    with translate_domain_errors():
        uc.execute(project_id, _actor(user))