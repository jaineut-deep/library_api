from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
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
