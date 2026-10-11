from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from .validators import (validate_day_existence, validate_day_with_month, validate_month_range, validate_book_amount,
                         validate_birth_year, validate_publication)


class Author(models.Model):
    first_name = models.CharField(max_length=25, verbose_name="Имя", help_text="Укажите имя автора")
    surname = models.CharField(max_length=35, verbose_name="Фамилия", help_text="Укажите фамилию автора")
    middle_name = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        verbose_name="Отчество",
        help_text="Укажите отчество автора"
    )
    birth_day = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name="День рождения",
        blank=True,
        null=True,
        help_text="Укажите день рождения автора",
    )
    birth_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Месяц рождения",
        blank=True,
        null=True,
        help_text="Укажите месяц рождения автора",
    )
    birth_year = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
        verbose_name="Год рождения",
        help_text="Укажите год рождения автора",
    )
    is_bc_era = models.BooleanField(
        default=False,
        verbose_name="До нашей эры",
        help_text="Отметьте, если автор до н. э.",
    )

    def __str__(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.surname}"
        return f"{self.first_name} {self.surname}"

    class Meta:
        verbose_name = "автор"
        verbose_name_plural = "авторы"
        ordering = ["surname"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(birth_day__isnull=True) | models.Q(birth_day__gte=1, birth_day__lte=31),
                name="author_birth_day_valid_range",
            ),
            models.CheckConstraint(
                condition=models.Q(birth_month__isnull=True) | models.Q(birth_month__gte=1, birth_month__lte=12),
                name="author_birth_month_valid_range",
            ),
            models.CheckConstraint(
                condition=models.Q(birth_year__gte=1, birth_year__lte=9999),
                name="author_birth_year_check",
            ),
            models.CheckConstraint(
                condition=models.Q(birth_day__isnull=True) | models.Q(birth_month__isnull=False),
                name="author_birth_day_requires_month",
            )
        ]

    def clean(self):
        super().clean()

        try:
            astronomical_year = self.to_astronomical_year(self.birth_year)
            validate_day_existence(self, astronomical_year)
            validate_day_with_month(self)
            validate_month_range(self)
            validate_birth_year(self)
        except ValidationError:
            return
        except ValueError:
            return
        else:
            self.birth_year = self.to_astronomical_year(self.birth_year)

    def save(self, *args, **kwargs) -> None:
        """
        Переопределённый метод save() для сохранения результата после валидации полей модели Author
        :param args:
        :param kwargs:
        :return: None
        """

        self.full_clean()
        return super().save(*args, **kwargs)

    @staticmethod
    def is_leap_year(year: int) -> bool:
        """
        Метод проверяющий, является ли указанный год високосным.
        :param year: int
        :return: bool
        """

        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    @property
    def year(self) -> int:
        """
        Геттер, возвращающий историческое значение года из базы данных
        :return: int
        """

        if self.birth_year < 1:
            return (self.birth_year - 1) * (-1)
        return self.birth_year

    def to_astronomical_year(self, year: int) -> int | None:
        """
        Метод, принимающий
        :param year: int
        :return: int
        """

        if year < 1:
            raise ValueError("Год должен быть положительным")
        if self.is_bc_era:
            return 1 - year
        elif not self.is_bc_era:
            return year


class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название", help_text="Укажите название книги")
    genre = models.CharField(max_length=35, verbose_name="Жанр", help_text="Укажите название жанра")
    is_bc_era = models.BooleanField(
        default=False,
        verbose_name="До нашей эры",
        help_text="Отметьте, если книга опубликована впервые до н. э.",
    )
    publication_year = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
        blank=True,
        null=True,
        verbose_name="Год публикации",
        help_text="Укажите год публикации",
    )
    author = models.ForeignKey(
        to=Author,
        on_delete=models.CASCADE,
        related_name="books",
        verbose_name="Автор",
        help_text="Выберите автора",
    )
    amount = models.IntegerField(verbose_name="Всего", help_text="Укажите количество всех экземпляров книги")

    def __str__(self):
        return f"{self.title} - {self.amount}"

    class Meta:
        verbose_name = "книга"
        verbose_name_plural = "книги"
        ordering = ["author"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(publication_year__gte=1, publication_year__lte=9999),
                name="book_publication_year_check",
            ),
            models.CheckConstraint(
                condition=models.Q(amount__gte=1),
                name="book_amount_check",
            ),
        ]

    def clean(self):
        super().clean()

        validate_publication(self)
        validate_book_amount(self)

    def save(self, *args, **kwargs) -> None:
        """
        Переопределённый метод save() для сохранения результата после валидации полей модели Book
        :param args:
        :param kwargs:
        :return: None
        """

        self.full_clean()
        return super().save(*args, **kwargs)


class Publication(models.Model):
    edition = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
        verbose_name="Год издания",
        help_text="Укажите год издания",
    )
    publisher = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Издательство",
        help_text="Укажите издательство"
    )
    publication_place = models.CharField(
        max_length=35,
        verbose_name="Место публикации",
        help_text="Укажите место публикации",
    )
    book = models.ForeignKey(
        to=Book,
        on_delete=models.CASCADE,
        related_name="publications",
        verbose_name="Книга",
        help_text="Выберите книгу",
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество", help_text="Укажите количество публикаций")

    def __str__(self):
        return f"{self.book}, {self.publisher} {self.edition}"

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "публикации"
        ordering = ["publisher"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(edition__gte=1, edition__lte=9999),
                name="publication_edition_check",
            )
        ]

    def clean(self):
        super().clean()

        validate_publication(self)
        validate_book_amount(self)

    def save(self, *args, **kwargs) -> None:
        """
        Переопределённый метод save() для сохранения результата после валидации полей модели Publication
        :param args:
        :param kwargs:
        :return: None
        """

        self.full_clean()
        return super().save(*args, **kwargs)
