from typing import Optional, Protocol

from app.domain.article import ContentBlock


class ArticleContentRepository(Protocol):
    def insert(self, article_id: int, blocks: list[ContentBlock]) -> None: ...

    def get(self, article_id: int) -> Optional[list[ContentBlock]]: ...

    def delete(self, article_id: int) -> None: ...