from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Audiobook, Issue, Publication


def catalog_directory_path(instance: Publication | Issue | Audiobook, filename: str) -> str:
    model_class = type(instance)

    return f"fund/{model_class.__name__.lower()}/{instance.book.genre}/{instance.book.title}/"
