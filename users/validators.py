from __future__ import annotations
from typing import TYPE_CHECKING
from django.core.exceptions import ValidationError

if TYPE_CHECKING:
    from .models import LendingBook


def validate_count_renewal(obj: LendingBook) -> None:
    if obj.count_renewal > 2:
        raise ValidationError({"count_renewal": "У выдачи не может быть больше двух продлений"})
