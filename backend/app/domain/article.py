import re
import unicodedata
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class ArticleStatus:
    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"


@dataclass(frozen=True)
class ContentBlock:
    id: str
    type: str  # text | image | code | quote
    data: dict = field(default_factory=dict)


@dataclass
class Article:
    id: int
    owner_id: uuid.UUID
    title: str
    slug: str
    status: str
    tags: list[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ArticleWithContent:
    article: Article
    blocks: list[ContentBlock]


def make_slug(title: str) -> str:
    text = title.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:150] or "bai-viet"
    return f"{text}-{uuid.uuid4().hex[:6]}"