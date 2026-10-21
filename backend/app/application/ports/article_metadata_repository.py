import uuid
from typing import Optional, Protocol

from app.domain.article import Article


class ArticleMetadataRepository(Protocol):
    def create_pending(
        self, owner_id: uuid.UUID, title: str, slug: str, tags: list[str]
    ) -> int: ...

    def set_status(self, article_id: int, status: str) -> None: ...

    def get(self, article_id: int) -> Optional[Article]: ...

    def search(
        self, q: Optional[str], tag: Optional[str], limit: int, offset: int
    ) -> tuple[list[Article], int]: ...