import uuid

import pytest

from app.application.use_cases.article_use_cases import (
    CreateArticle,
    CreateArticleCommand,
    GetArticle,
)
from app.domain.article import Article, ContentBlock
from app.domain.errors import ArticleNotFound, ContentMissing, StoreUnavailable


class FakeMeta:
    def __init__(self):
        self.rows = {}

    def create_pending(self, owner_id, title, slug, tags):
        article_id = len(self.rows) + 1
        self.rows[article_id] = Article(article_id, owner_id, title, slug, "pending", tags)
        return article_id

    def set_status(self, article_id, status):
        self.rows[article_id].status = status

    def get(self, article_id):
        return self.rows.get(article_id)


class FakeContent:
    def __init__(self, fail_insert=False):
        self.fail_insert = fail_insert
        self.docs = {}

    def insert(self, article_id, blocks):
        if self.fail_insert:
            raise RuntimeError("mongo down")
        self.docs[article_id] = blocks

    def get(self, article_id):
        return self.docs.get(article_id)

    def delete(self, article_id):
        self.docs.pop(article_id, None)


def _cmd():
    return CreateArticleCommand(
        owner_id=uuid.uuid4(),
        title="Tiêu đề",
        tags=["a"],
        blocks=[ContentBlock(id="b1", type="text", data={"value": "x"})],
    )


def test_happy_path_publishes():
    meta, content = FakeMeta(), FakeContent()
    result = CreateArticle(meta, content).execute(_cmd())
    assert result.status == "published"
    assert 1 in content.docs


def test_mongo_failure_marks_article_failed():
    meta, content = FakeMeta(), FakeContent(fail_insert=True)
    with pytest.raises(StoreUnavailable):
        CreateArticle(meta, content).execute(_cmd())
    assert meta.rows[1].status == "failed"


def test_get_missing_content_raises_content_missing():
    meta, content = FakeMeta(), FakeContent()
    CreateArticle(meta, content).execute(_cmd())
    content.docs.clear()  # mô phỏng document Mongo bị mất
    with pytest.raises(ContentMissing):
        GetArticle(meta, content).execute(1)


def test_get_unknown_article_raises_not_found():
    with pytest.raises(ArticleNotFound):
        GetArticle(FakeMeta(), FakeContent()).execute(9999)