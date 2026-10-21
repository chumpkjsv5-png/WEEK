import uuid
from datetime import datetime
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_TAGS = 10
MAX_TAG_LEN = 50


class _Block(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])


class TextBlock(_Block):
    type: Literal["text"] = "text"
    value: str = Field(min_length=1, max_length=20000)


class ImageBlock(_Block):
    type: Literal["image"] = "image"
    url: str = Field(min_length=1, max_length=2000)
    alt: str = Field(default="", max_length=300)
    caption: Optional[str] = Field(default=None, max_length=300)


class CodeBlock(_Block):
    type: Literal["code"] = "code"
    language: str = Field(default="text", max_length=30)
    value: str = Field(min_length=1, max_length=20000)


class QuoteBlock(_Block):
    type: Literal["quote"] = "quote"
    value: str = Field(min_length=1, max_length=2000)
    author: Optional[str] = Field(default=None, max_length=100)


ContentBlock = Annotated[
    Union[TextBlock, ImageBlock, CodeBlock, QuoteBlock],
    Field(discriminator="type"),
]


class ArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    tags: list[str] = Field(default_factory=list)
    blocks: list[ContentBlock] = Field(min_length=1, max_length=100)

    @field_validator("title")
    @classmethod
    def _strip_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Tiêu đề không được để trống")
        return v

    @field_validator("tags")
    @classmethod
    def _normalize_tags(cls, v: list[str]) -> list[str]:
        result: list[str] = []
        for raw in v:
            name = raw.strip().lower()
            if not name:
                continue
            if len(name) > MAX_TAG_LEN:
                raise ValueError(f"Tag tối đa {MAX_TAG_LEN} ký tự")
            if name not in result:
                result.append(name)
        if len(result) > MAX_TAGS:
            raise ValueError(f"Tối đa {MAX_TAGS} tag mỗi bài")
        return result


class ArticleBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: uuid.UUID
    title: str
    slug: str
    status: str
    tags: list[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("tags", mode="before")
    @classmethod
    def _tag_names(cls, v):
        return sorted(t.name if hasattr(t, "name") else t for t in v)


class ArticleDetail(ArticleBrief):
    blocks: list[dict]


class ArticleBriefList(BaseModel):
    items: list[ArticleBrief]
    total: int