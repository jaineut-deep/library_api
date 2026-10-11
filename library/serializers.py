from django.utils import timezone
from rest_framework import serializers
from .models import Author, Book, Publication


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"

    def validate(self, data):
        birth_day = data.get("birth_day")
        birth_month = data.get("birth_month")
        birth_year = data.get("birth_year")
        is_bc_era = data.get("is_bc_era")

        if not ((birth_day is None) | 1 <= birth_day <= 31):
            raise serializers.ValidationError(
                {"birth_day": "День должен быть положительным и не больше 31"}
            )

        if not ((birth_month is None) | 1 <= birth_month <= 12):
            raise serializers.ValidationError(
                {"birth_month": "Месяц должен быть положительным и не больше 12"}
            )

        if is_bc_era and not (1 <= birth_year <= 9999):
            raise serializers.ValidationError(
                {"birth_year": "Указанный год не положительный или выше максимального значения"}
            )

        if not is_bc_era and not (1 <= birth_year <= timezone.now().year):
            raise serializers.ValidationError({"birth_year": "Год не может быть отрицательным или в будущем"})
        elif is_bc_era and not (1 <= birth_year <= 9999):
            raise serializers.ValidationError(
                {"birth_year": "Год не может быть отрицательным или выше максимума значений"}
            )

        if not ((birth_day is None) | (birth_month is not None)):
            raise serializers.ValidationError({"birth_day": "Нельзя указать день без месяца"})

        return data


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"

    def validate(self, data):
        publication_year = data.get("publication_year")
        amount = data.get("amount")
        is_bc_era = data.get("is_bc_era")

        if not is_bc_era and not (1 <= publication_year <= timezone.now().year):
            raise serializers.ValidationError({"publication_year": "Год публикации не может быть отрицательным или в будущем"})
        elif is_bc_era and not (1 <= publication_year <= 9999):
            raise serializers.ValidationError(
                {"publication_year": "Год публикации не может быть отрицательным или выше максимума значений"}
            )

        if amount < 0:
            raise serializers.ValidationError({"amount": "Количество книг не может быть отрицательным"})

        return data


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = "__all__"

    def validate(self, data):
        edition = data.get("edition")
        quantity = data.get("quantity")

        if not (1 <= edition <= timezone.now().year):
            raise serializers.ValidationError({"edition": "Год издания не может быть отрицательным или в будущем"})

        if quantity < 0:
            raise serializers.ValidationError({"quantity": "Количество публикаций не может быть отрицательным"})

        return data
