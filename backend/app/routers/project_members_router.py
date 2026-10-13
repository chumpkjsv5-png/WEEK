# app/routers/project_members.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.project_member_schema import MemberCreate, MemberOut, UserSearchOut
from app.services import project_member_service as service

router = APIRouter(prefix="/projects/{project_id}/members", tags=["project-members"])


@router.get("", response_model=List[MemberOut])
def list_members(project_id: int, db: Session = Depends(get_db)):
    return service.list_members(db, project_id)


# Khai báo trước các route có path param động (/{user_id})
@router.get("/search", response_model=List[UserSearchOut])
def search_users_to_add(
    project_id: int,
    q: str = Query(..., min_length=1, max_length=50),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return service.search_users_to_add(db, project_id, q, limit)


@router.post("", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def add_member(project_id: int, payload: MemberCreate, db: Session = Depends(get_db)):
    return service.add_member(db, project_id, payload.user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(project_id: int, user_id: UUID, db: Session = Depends(get_db)):
    service.remove_member(db, project_id, user_id)