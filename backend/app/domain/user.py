import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class UserSummary:
    """Minimum information required for selecting a person (excluding role and password)."""
    id: uuid.UUID
    full_name: str
    email: str