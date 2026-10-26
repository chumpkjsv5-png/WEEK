import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthUser:
    """The user has been authenticated. The router reads the ID and role, so these attributes must be preserved.."""
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool


@dataclass(frozen=True)
class UserCredentials:
    id: uuid.UUID
    password_hash: str
    is_active: bool
