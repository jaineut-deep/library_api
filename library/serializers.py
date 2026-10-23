from typing import Any

from django.utils import timezone
from rest_framework import serializers

from users.models import LendingBook
from users.serializers import LendingBookSerializer

from .models import Author, Book, Publication, Issue, Audiobook


class BookSerializer(serializers.ModelSerializer):
    lendings = serializers.SerializerMethodField()

    def get_lendings(self, instance: Book) -> list | None | Any:
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return []

        query_set = LendingBook.objects.filter(publication__book=instance)

        if request and request.user.is_authenticated and not request.user.is_staff:
            query_set = query_set.filter(member=request.user)
            return LendingBookSerializer(query_set, many=True, context=self.context).data
        elif request and request.user.is_authenticated and request.user.is_staff:
            return LendingBookSerializer(query_set, many=True, context=self.context).data

        return []

    class Meta:
        model = Book
        fields = ["id", "title", "genre", "is_bc_era", "publication_year", "author", "amount", "lendings"]

    def validate(self, data: Any) -> Any:
        values = {}

        if self.instance is not None:
            values = {
                "title": self.instance.title,
                "genre": self.instance.genre,
                "is_bc_era": self.instance.is_bc_era,
                "publication_year": self.instance.publication_year,
                "author": self.instance.author,
                "amount": self.instance.amount,
            }

        values.update(data)

        publication_year = values.get("publication_year")
        amount = values.get("amount")
        is_bc_era = values.get("is_bc_era")

        if publication_year is None or not (-9998 <= publication_year <= 9999):
            raise serializers.ValidationError(
                {"publication_year": "Год публикации вне допустимого диапазона значений"}
            )

        if not is_bc_era and publication_year > timezone.now().year:
            raise serializers.ValidationError({"publication_year": "Год опубликования не может быть в будущем"})

        if isinstance(amount, int):
            if amount < 0:
                raise serializers.ValidationError({"amount": "Количество книг не может быть отрицательным"})

        return data

    def to_internal_value(self, data: Any) -> Any:
        validated_data = super().to_internal_value(data)
        publication_year = validated_data.get("publication_year", None)
        is_bc_era = validated_data.get("is_bc_era", None)

        if publication_year is not None and is_bc_era is not None:
            if not is_bc_era and not (1 <= publication_year <= timezone.now().year):
                raise serializers.ValidationError(
                    {"publication_year": "Год не может быть отрицательным или в будущем"}
                )
            elif is_bc_era and not (1 <= publication_year <= 9999):
                raise serializers.ValidationError(
                    {"publication_year": "Год не может быть отрицательным или выше максимума значений"}
                )

            if is_bc_era:
                validated_data["publication_year"] = 1 - publication_year
            if not is_bc_era:
                validated_data["publication_year"] = publication_year

        return validated_data

    def to_representation(self, instance: Book) -> Any:
        data = super().to_representation(instance)
        astro = instance.publication_year
        if astro is None:
            data["is_bc_era"] = False
            return data
        if astro <= 0:
            data["publication_year"] = 1 - astro
            data["is_bc_era"] = True
        else:
            data["publication_year"] = astro
            data["is_bc_era"] = False

        return data


class AuthorSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()
    books = BookSerializer(many=True, required=False)

    def get_book_count(self, instance: Author) -> int:
        return instance.books.count()

    class Meta:
        model = Author
        fields = [
            "first_name",
            "surname",
            "middle_name",
            "birth_day",
            "birth_month",
            "birth_year",
            "is_bc_era",
            "books",
            "book_count",
        ]

    def validate(self, data: dict) -> dict:
        values = {}

        if self.instance is not None:
            values = {
                "first_name": self.instance.first_name,
                "surname": self.instance.surname,
                "middle_name": self.instance.middle_name,
                "birth_day": self.instance.birth_day,
                "birth_month": self.instance.birth_month,
                "birth_year": self.instance.birth_year,
                "is_bc_era": self.instance.is_bc_era,
            }

        values.update(data)

        birth_day = values.get("birth_day")
        birth_month = values.get("birth_month")
        birth_year = values.get("birth_year")
        is_bc_era = values.get("is_bc_era")

        if birth_day is None or not (1 <= birth_day <= 31):
            raise serializers.ValidationError({"birth_day": "День должен быть положительным и не больше 31"})

        if birth_month is None or not (1 <= birth_month <= 12):
            raise serializers.ValidationError({"birth_month": "Месяц должен быть положительным и не больше 12"})

        if birth_year is None or not (-9998 <= birth_year <= 9999):
            raise serializers.ValidationError({"birth_year": "Год вне допустимого диапазона значений"})

        if not is_bc_era and birth_year > timezone.now().year:
            raise serializers.ValidationError({"birth_year": "Год рождения не может быть в будущем"})

        if birth_day is not None and birth_month is None:
            raise serializers.ValidationError({"birth_day": "Нельзя указать день без месяца"})

        return data

    def to_internal_value(self, data: Any) -> Any:
        validated_data = super().to_internal_value(data)
        birth_year = validated_data.get("birth_year", None)
        is_bc_era = validated_data.get("is_bc_era", None)

        if birth_year is not None and is_bc_era is not None:
            if not is_bc_era and not (1 <= birth_year <= timezone.now().year):
                raise serializers.ValidationError({"birth_year": "Год не может быть отрицательным или в будущем"})
            elif is_bc_era and not (1 <= birth_year <= 9999):
                raise serializers.ValidationError(
                    {"birth_year": "Год не может быть отрицательным или выше максимума значений"}
                )

            if is_bc_era:
                validated_data["birth_year"] = 1 - birth_year
            if not is_bc_era:
                validated_data["birth_year"] = birth_year

        return validated_data

    def to_representation(self, instance: Author) -> Any:
        data = super().to_representation(instance)
        astro = instance.birth_year
        if astro is None:
            data["is_bc_era"] = False
            return data
        if astro <= 0:
            data["birth_year"] = 1 - astro
            data["is_bc_era"] = True
        else:
            data["birth_year"] = astro
            data["is_bc_era"] = False

        return data


class PublicationSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True)

    class Meta:
        model = Publication
        fields = ["edition", "publisher", "publication_place", "book", "quantity"]
        read_only_fields = ["book"]

    def validate(self, data: Any) -> Any:
        edition = data.get("edition")
        quantity = data.get("quantity")

        if not (1 <= edition <= timezone.now().year):
            raise serializers.ValidationError({"edition": "Год издания не может быть отрицательным или в будущем"})

        if quantity < 0:
            raise serializers.ValidationError({"quantity": "Количество публикаций не может быть отрицательным"})

        return data


class IssueSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True)

    class Meta:
        model = Issue
        fields = ["book", "issue_date", "volume_number", "issue_number", "quantity"]
        read_only_fields = ["book"]

    def validate(self, data: Any) -> Any:
        quantity = data.get("quantity")

        if quantity < 0:
            raise serializers.ValidationError({"quantity": "Количество выпусков журнала не может быть отрицательным"})

        return data


class IssueMemberSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True)

    class Meta:
        model = Issue
        fields = ["book", "issue_date", "volume_number", "issue_number"]
        read_only_fields = ["book"]


class AudiobookSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True)

    class Meta:
        model = Audiobook
        fields = ["book", "narrator", "language", "duration", "format"]
        read_only_fields = ["book"]
