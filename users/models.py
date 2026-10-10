from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models
from .validators import validate_count_renewal


class CustomUser(AbstractUser):
    """Кастомный класс для представления пользователей библиотеки"""

    email = models.EmailField(unique=True, verbose_name="Email", help_text="Укажите свой email")
    phone_number = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Номер телефона", help_text="Укажите свой номер телефона"
    )
    city = models.CharField(max_length=35, blank=True, null=True, verbose_name="Город", help_text="Укажите свой город")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Фото", help_text="Добавьте свое фото"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class LendingBook(models.Model):
    """Класс для представления выдачи книги читателям"""

    publication = models.ForeignKey(
        to="library.Publication",
        on_delete=models.CASCADE,
        related_name="lendings",
        verbose_name="Публикация",
        help_text="Укажите публикацию книги",
    )
    member = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name="lendings",
        verbose_name="Читатель",
        help_text="Укажите читателя выдачи",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    count_renewal = models.PositiveIntegerField(
        validators=[MaxValueValidator(2)],
        default=0,
        verbose_name="Количество продлений",
    )

    def __str__(self):
        return f"{self.member} - {self.updated_at.date()}, продлений: {self.count_renewal}"

    class Meta:
        verbose_name = "выдача_книги"
        verbose_name_plural = "выдача_книг"
        ordering = ["count_renewal"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(count_renewal__lte=2),
                name="lendingbook_count_renewal_check",
            )
        ]

    def clean(self):
        super().clean()

        validate_count_renewal(self)

    def save(self, *args, **kwargs) -> None:
        """
        Переопределённый метод save() для сохранения результата после валидации полей модели LandingBook
        :param args:
        :param kwargs:
        :return: None
        """

        self.full_clean()
        return super().save(*args, **kwargs)
