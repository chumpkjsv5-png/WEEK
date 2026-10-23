from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app import composition
from app.adapters.inbound.http.error_translation import translate_domain_errors
from app.application.use_cases.auth_use_cases import AuthenticateToken
from app.core.exceptions import ForbiddenError
from app.domain.auth import AuthUser

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    uc: AuthenticateToken = Depends(composition.get_authenticate_token),
) -> AuthUser:
    token = creds.credentials if creds else None
    with translate_domain_errors():
        return uc.execute(token)


def require_role(*roles: str):
    def checker(user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if user.role not in roles:
            raise ForbiddenError("Bạn không có quyền thực hiện thao tác này")
        return user

    return checker
