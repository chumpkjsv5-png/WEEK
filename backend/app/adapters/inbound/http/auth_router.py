from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app import composition
from app.adapters.inbound.http.dependencies import get_current_user
from app.adapters.inbound.http.error_translation import translate_domain_errors
from app.application.use_cases.auth_use_cases import Login
from app.domain.auth import AuthUser
from app.schemas.auth_schema import LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

LoginUC = Annotated[Login, Depends(composition.get_login)]
CurrentUser = Annotated[AuthUser, Depends(get_current_user)]


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, uc: LoginUC):
    with translate_domain_errors():
        result = uc.execute(data.email, data.password)

    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(_: CurrentUser):
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser):
    return user
