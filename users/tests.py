from datetime import datetime, timezone

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIClient

from library.models import Author, Book, Publication

from .models import CustomUser, LendingBook
from .serializers import LendingBookMemberSerializer, LendingBookSerializer, LendingBookStaffSerializer


class LendingTestCase(TestCase):

    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(username="user_test", email="test@example.com", password="qwerty")
        self.user_owner = CustomUser.objects.create_user(
            username="owner_user", email="owner@example.com", password="123qwe"
        )
        self.user_moder = CustomUser.objects.create_user(
            username="moder_user", email="moder@example.com", password="qwe123", is_staff=True
        )
        self.author_one = Author.objects.create(
            first_name="Федор",
            surname="Достоевский",
            middle_name="Михайлович",
            birth_day=11,
            birth_month=11,
            birth_year=1821,
        )
        self.book_one = Book.objects.create(
            title="Идиот",
            genre="Роман",
            is_bc_era=False,
            publication_year=1868,
            author=self.author_one,
            amount=2,
        )
        self.publication_one = Publication.objects.create(
            edition=2022,
            publisher="ЛИТ-Пресс",
            publication_place="С-Петербург",
            book=self.book_one,
            quantity=1,
        )
        self.publication_two = Publication.objects.create(
            edition=2015,
            publisher="ЭКСМО",
            publication_place="Москва",
            book=self.book_one,
            quantity=1,
        )
        self.lending_one = LendingBook.objects.create(
            publication=self.publication_one,
            member=self.user,
            created_at=datetime(2026, 10, 16, 14, 30, tzinfo=timezone.utc),
            updated_at=datetime(2026, 10, 16, 14, 30, tzinfo=timezone.utc),
            count_renewal="zero",
            status=True,
        )

        self.client: APIClient = APIClient()

    def test_create_lending_user(self) -> None:
        self.client.force_authenticate(user=self.user_owner)
        url = reverse("users:lending-list")
        data = {
            "publication": self.publication_two.pk,
            "member": self.user_owner.pk,
        }

        response = self.client.post(url, data)
        lending_data = LendingBook.objects.get(publication=self.publication_two)
        serialized_lending = LendingBookSerializer(lending_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), serialized_lending.data)

    def test_list_lending_user(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("users:lending-list")
        response: DRFResponse = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        lending_data = LendingBook.objects.filter(member=self.user)
        serialized_lending = LendingBookMemberSerializer(lending_data, many=True)

        page_size = response.data.get("page_size", 2)
        expected_count = min(len(serialized_lending.data), page_size)
        self.assertEqual(len(response.data["results"]), expected_count)

    def test_retrieve_lending_user(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("users:lending-detail", args=(self.lending_one.pk,))
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("publication"), self.lending_one.publication_id)

    def test_update_lending_user(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("users:lending-detail", args=(self.lending_one.pk,))
        data = {"status": False}

        response = self.client.patch(url, data)

        lending_data = response.json()
        self.lending_one.refresh_from_db()
        serialized_lending = LendingBookStaffSerializer(self.lending_one)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(lending_data.get("status"), serialized_lending.data.get("status"))

    def tearDown(self) -> None:
        Author.objects.all().delete()
