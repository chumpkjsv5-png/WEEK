from datetime import datetime, timezone
from typing import Optional

from pymongo.collection import Collection

SCHEMA_VERSION = 1


def insert_content(col: Collection, article_id: int, blocks: list[dict]) -> None:
    now = datetime.now(timezone.utc)
    col.insert_one(
        {
            "article_id": article_id,
            "schema_version": SCHEMA_VERSION,
            "blocks": blocks,
            "created_at": now,
            "updated_at": now,
        }
    )


def get_content(col: Collection, article_id: int) -> Optional[list[dict]]:
    doc = col.find_one({"article_id": article_id}, {"_id": 0, "blocks": 1})
    return None if doc is None else doc["blocks"]


def delete_content(col: Collection, article_id: int) -> None:
    col.delete_one({"article_id": article_id})