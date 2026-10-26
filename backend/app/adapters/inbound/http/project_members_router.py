from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app import composition
from app.adapters.inbound.http.error_translation import translate_domain_errors
from app.application.use_cases.project_member_use_cases import (
    AddMember,
    ListMembers,
    RemoveMember,
    SearchUsersToAdd,
)
from app.adapters.inbound.http.dependencies import get_current_user, require_role
from app.core.permissions import ADMIN, CAN_MANAGE, MANAGER
from app.domain.project import ProjectActor
from app.models.user_data import User
from app.schemas.project_member_schema import MemberCreate, MemberOut, UserSearchOut

router = APIRouter(prefix="/projects/{project_id}/members", tags=["project-members"])

CurrentUser = Annotated[User, Depends(get_current_user)]
ManagerUser = Annotated[User, Depends(require_role(*CAN_MANAGE))]

ListUC = Annotated[ListMembers, Depends(composition.get_list_members)]
SearchUC = Annotated[SearchUsersToAdd, Depends(composition.get_search_users_to_add)]
AddUC = Annotated[AddMember, Depends(composition.get_add_member)]
RemoveUC = Annotated[RemoveMember, Depends(composition.get_remove_member)]


def _actor(user: User) -> ProjectActor:
    return ProjectActor(
        id=user.id,
        is_admin=(user.role == ADMIN),
        is_manager=(user.role == MANAGER),
    )


@router.get("", response_model=List[MemberOut])
def list_members(project_id: int, user: CurrentUser, uc: ListUC):
    with translate_domain_errors():
        return uc.execute(project_id)


# Khai báo trước các route có path param động (/{user_id})
@router.get("/search", response_model=List[UserSearchOut])
def search_users_to_add(
    project_id: int,
    user: ManagerUser,
    uc: SearchUC,
    q: str = Query(..., min_length=1, max_length=50),
    limit: int = Query(10, ge=1, le=50),
):
    with translate_domain_errors():
        return uc.execute(project_id, q, _actor(user), limit)


@router.post("", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def add_member(project_id: int, payload: MemberCreate, user: ManagerUser, uc: AddUC):
    with translate_domain_errors():
        return uc.execute(project_id, payload.user_id, _actor(user))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(project_id: int, user_id: UUID, user: ManagerUser, uc: RemoveUC):
    with translate_domain_errors():
        uc.execute(project_id, user_id, _actor(user))
