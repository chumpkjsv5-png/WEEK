from datetime import datetime, timezone
from typing import Optional

from pymongo.collection import Collection

from app.domain.article import ContentBlock

SCHEMA_VERSION = 1


def _to_doc(b: ContentBlock) -> dict:
    return {"id": b.id, "type": b.type, **b.data}


def _from_doc(d: dict) -> ContentBlock:
    d = dict(d)
    return ContentBlock(id=d.pop("id"), type=d.pop("type"), data=d)


class MongoArticleContentRepository:
    def __init__(self, col: Collection):
        self.col = col

    def insert(self, article_id: int, blocks: list[ContentBlock]) -> None:
        now = datetime.now(timezone.utc)
        self.col.insert_one(
            {
                "article_id": article_id,
                "schema_version": SCHEMA_VERSION,
                "blocks": [_to_doc(b) for b in blocks],
                "created_at": now,
                "updated_at": now,
            }
        )

    def get(self, article_id: int) -> Optional[list[ContentBlock]]:
        doc = self.col.find_one({"article_id": article_id}, {"_id": 0, "blocks": 1})
        return None if doc is None else [_from_doc(b) for b in doc["blocks"]]

    def delete(self, article_id: int) -> None:
        self.col.delete_one({"article_id": article_id})