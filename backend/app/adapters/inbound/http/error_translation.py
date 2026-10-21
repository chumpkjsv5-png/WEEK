from contextlib import contextmanager

from app.core.exceptions import (
    ContentMissingError,
    NotFoundError,
    StoreUnavailableError,
)
from app.domain.errors import ArticleNotFound, ContentMissing, StoreUnavailable


@contextmanager
def translate_domain_errors():
    try:
        yield
    except ArticleNotFound as e:
        raise NotFoundError(str(e), code="ARTICLE_NOT_FOUND") from e
    except ContentMissing as e:
        raise ContentMissingError(str(e)) from e
    except StoreUnavailable as e:
        raise StoreUnavailableError(str(e)) from e