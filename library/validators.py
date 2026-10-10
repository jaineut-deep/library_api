from __future__ import annotations
from django.utils import timezone
from typing import TYPE_CHECKING
from django.core.exceptions import ValidationError

if TYPE_CHECKING:
    from .models import Author, Book, Publication


def validate_birth_year(obj: Author) -> None:
    if not obj.is_bc_era and not (1 <= obj.birth_year <= timezone.now().year):
        raise ValidationError({"birth_year": "Год не может быть отрицательным или в будущем"})
    elif obj.is_bc_era and not (1 <= obj.birth_year <= 9999):
        raise ValidationError({"birth_year": "Год не может быть отрицательным или выше максимума значений"})


def validate_day_existence(obj: Author, astronomical_year: int) -> None:
    if obj.birth_day is not None:
        if obj.birth_day < 1:
            raise ValidationError({"birth_day": "День должен быть положительным"})
        else:
            days_in_month = [
                31, 29 if obj.is_leap_year(astronomical_year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
            ]

            if obj.birth_day is not None and not 1 <= obj.birth_day <= days_in_month[obj.birth_month -1]:
                raise ValidationError({
                    "birth_day": "Такого дня нет в указанном месяце и годе"
                })


def validate_day_with_month(obj: Author) -> None:
    if obj.birth_month is None:
            if obj.birth_day is not None:
                raise ValidationError({"birth_day": "Нельзя указать день без месяца."})


def validate_month_range(obj: Author) -> None:
    if not 1 <= obj.birth_month <= 12:
        raise ValidationError({"birth_month": "Месяц должен быть от 1 до 12"})


def validate_book_amount(obj: Book | Publication) -> None:
    if isinstance(obj, Book) & obj.amount < 0:
        raise ValidationError({"amount": "Количество книг не может быть отрицательным"})
    elif isinstance(obj, Publication) & obj.quantity < 0:
        raise ValidationError({"quantity": "Количество публикаций не может быть отрицательным"})


def validate_publication(obj: Book | Publication) -> None:
    if isinstance(obj, Book):
        if not obj.is_bc_era and not (1 <= obj.publication_year <= timezone.now().year):
            raise ValidationError({"publication_year": "Год публикации не может быть отрицательным или в будущем"})
        elif obj.is_bc_era and not (1 <= obj.publication_year <= 9999):
            raise ValidationError(
                {"publication_year": "Год публикации не может быть отрицательным или выше максимума значений"}
            )
    if isinstance(obj, Publication):
        if not (1 <= obj.edition <= timezone.now().year):
            raise ValidationError({"edition": "Год издания не может быть отрицательным или в будущем"})
