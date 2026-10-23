from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.utils import timezone

if TYPE_CHECKING:
    from .models import Author, Book, Publication, Issue


def validate_birth_year(obj: Author) -> None:
    if obj.is_bc_era is not None and not (-9998 <= obj.birth_year <= timezone.now().year):
        raise ValidationError({"birth_year": "Год не может быть ниже минимума значений или в будущем"})


def validate_day_existence(obj: Author, astronomical_year: int) -> None:
    if obj.birth_day is not None:
        if obj.birth_day < 1:
            raise ValidationError({"birth_day": "День должен быть положительным"})
        else:
            days_in_month = [
                31,
                29 if obj.is_leap_year(astronomical_year) else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ]

            if isinstance(obj.birth_month, int):
                if obj.birth_day is not None and not 1 <= obj.birth_day <= days_in_month[obj.birth_month - 1]:
                    raise ValidationError({"birth_day": "Такого дня нет в указанном месяце и годе"})


def validate_day_with_month(obj: Author) -> None:
    if obj.birth_month is None:
        if obj.birth_day is not None:
            raise ValidationError({"birth_day": "Нельзя указать день без месяца."})


def validate_month_range(obj: Author) -> None:
    if isinstance(obj.birth_month, int):
        if not 1 <= obj.birth_month <= 12:
            raise ValidationError({"birth_month": "Месяц должен быть от 1 до 12"})


def validate_book_amount(obj: Book | Publication | Issue) -> None:
    from .models import Book, Publication, Issue

    if isinstance(obj, Book):
        if obj.amount < 0:
            raise ValidationError({"amount": "Количество книг не может быть отрицательным"})
    elif isinstance(obj, Publication):
        if obj.quantity < 0:
            raise ValidationError({"quantity": "Количество публикаций не может быть отрицательным"})
    elif isinstance(obj, Issue):
        if obj.quantity < 0:
            raise ValidationError({"quantity": "Количество выпусков журнала не может быть отрицательным"})


def validate_publication(obj: Book | Publication) -> None:
    from .models import Book, Publication

    if isinstance(obj, Book):
        if isinstance(obj.publication_year, int):
            if obj.is_bc_era is not None and not (-9998 <= obj.publication_year <= timezone.now().year):
                raise ValidationError(
                    {"publication_year": "Год публикации не может быть ниже минимума значений или в будущем"}
                )

    if isinstance(obj, Publication):
        if not (1 <= obj.edition <= timezone.now().year):
            raise ValidationError({"edition": "Год издания не может быть отрицательным или в будущем"})


def validate_negative_year_bce(obj: Author | Book) -> None:
    from .models import Author, Book

    if isinstance(obj, Author):
        if not (obj.birth_year < 1 or not obj.is_bc_era):
            raise ValidationError(
                {"birth_year": "Значение эры и года не соответствуют самой эре"}
            )

    if isinstance(obj, Book):
        if not (obj.publication_year < 1 or not obj.is_bc_era):
            raise ValidationError(
                {"birth_year": "Значение эры и года не соответствуют самой эре"}
            )
