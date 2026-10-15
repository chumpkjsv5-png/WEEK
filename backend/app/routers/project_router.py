from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_role
from app.core.permissions import ADMIN_ONLY, CAN_MANAGE
from app.database import get_db
from app.models.user_data import User
from app.schemas.project_schema import (
    ProjectCreate, ProjectUpdate, ProjectOut, ProjectListOut, ProjectFilterParams,
)
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
ManagerUser = Annotated[User, Depends(require_role(*CAN_MANAGE))]
AdminUser = Annotated[User, Depends(require_role(*ADMIN_ONLY))]


@router.get("", response_model=ProjectListOut)
def get_projects(
    params: Annotated[ProjectFilterParams, Query()],
    db: DbSession,
    user: CurrentUser,
):
    return project_service.list_projects(db, **params.model_dump())


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: DbSession, user: CurrentUser):
    return project_service.get_project(db, project_id)


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: DbSession, user: ManagerUser):
    return project_service.create_project(db, payload, user)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int, payload: ProjectUpdate, db: DbSession, user: ManagerUser
):
    return project_service.update_project(db, project_id, payload, user)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: DbSession, user: ManagerUser):
    project_service.delete_project(db, project_id, user)