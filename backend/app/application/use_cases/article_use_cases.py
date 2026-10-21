import logging
import uuid
from dataclasses import dataclass
from typing import Callable, Optional

from app.application.ports.article_content_repository import ArticleContentRepository
from app.application.ports.article_metadata_repository import ArticleMetadataRepository
from app.domain.article import (
    Article,
    ArticleStatus,
    ArticleWithContent,
    ContentBlock,
    make_slug,
)
from app.domain.errors import ArticleNotFound, ContentMissing, StoreUnavailable

logger = logging.getLogger(__name__)

DEFAULT_ARTICLE_LIMIT = 10
MAX_ARTICLE_LIMIT = 50


def _best_effort(fn: Callable, *args, what: str) -> None:
    try:
        fn(*args)
    except Exception:
        logger.exception("%s thất bại, cần job đối soát dọn", what)


@dataclass(frozen=True)
class CreateArticleCommand:
    owner_id: uuid.UUID
    title: str
    tags: list[str]
    blocks: list[ContentBlock]


class CreateArticle:
    def __init__(self, meta: ArticleMetadataRepository, content: ArticleContentRepository):
        self.meta = meta
        self.content = content

    def execute(self, cmd: CreateArticleCommand) -> Article:
        # Bước 1: SQL là nguồn sự thật, ghi trước với trạng thái pending
        article_id = self.meta.create_pending(
            cmd.owner_id, cmd.title, make_slug(cmd.title), cmd.tags
        )

        # Bước 2: ghi nội dung vào Mongo
        try:
            self.content.insert(article_id, cmd.blocks)
        except Exception:
            logger.exception("Mongo insert failed, article_id=%s", article_id)
            _best_effort(
                self.meta.set_status, article_id, ArticleStatus.FAILED,
                what=f"Đánh dấu failed article_id={article_id}",
            )
            raise StoreUnavailable("Không lưu được nội dung bài viết")

        # Bước 3: xác nhận published; lỗi thì bù trừ bằng cách xóa nội dung Mongo
        try:
            self.meta.set_status(article_id, ArticleStatus.PUBLISHED)
        except Exception:
            logger.exception("SQL publish failed, article_id=%s", article_id)
            _best_effort(
                self.content.delete, article_id,
                what=f"Bù trừ xóa Mongo article_id={article_id}",
            )
            raise StoreUnavailable("Không hoàn tất được bài viết")

        return self.meta.get(article_id)


class GetArticle:
    def __init__(self, meta: ArticleMetadataRepository, content: ArticleContentRepository):
        self.meta = meta
        self.content = content

    def execute(self, article_id: int) -> ArticleWithContent:
        article = self.meta.get(article_id)
        if article is None or article.status != ArticleStatus.PUBLISHED:
            raise ArticleNotFound("Bài viết không tồn tại")

        try:
            blocks = self.content.get(article_id)
        except Exception:
            logger.exception("Mongo read failed, article_id=%s", article_id)
            raise StoreUnavailable("Không đọc được nội dung bài viết")

        if blocks is None:
            logger.error(
                "CONTENT_MISSING: article_id=%s có ở SQL nhưng thiếu ở Mongo", article_id
            )
            raise ContentMissing("Bài viết tồn tại nhưng nội dung bị thiếu")

        return ArticleWithContent(article=article, blocks=blocks)


class SearchArticles:
    def __init__(self, meta: ArticleMetadataRepository):
        self.meta = meta

    def execute(
        self,
        q: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = DEFAULT_ARTICLE_LIMIT,
        offset: int = 0,
    ) -> dict:
        limit = min(max(limit, 1), MAX_ARTICLE_LIMIT)
        offset = max(offset, 0)
        items, total = self.meta.search(q, tag, limit, offset)
        return {"items": items, "total": total}