from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.project_schema import (
    ProjectCreate, ProjectUpdate, ProjectOut, ProjectListOut, ProjectFilterParams,
)
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectListOut)
def get_projects(
    params: Annotated[ProjectFilterParams, Query()],
    db: Session = Depends(get_db),
):
    items, total = project_service.list_projects(db, **params.model_dump())
    return {"items": items, "total": total}


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return project_service.get_project(db, project_id)


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    return project_service.create_project(db, payload)


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    return project_service.update_project(db, project_id, payload)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project_service.delete_project(db, project_id)