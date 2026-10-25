from datetime import date, datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response as DRFResponse
from rest_framework.test import APIClient

from users.models import CustomUser

from .models import Audiobook, Author, Book, Issue, Publication
from .serializers import AudiobookSerializer, AuthorSerializer, BookSerializer, IssueSerializer, PublicationSerializer


class BookTestCase(TestCase):

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
        self.author_two = Author.objects.create(
            first_name="Марк",
            surname="Цицерон",
            middle_name="Туллий",
            birth_day=3,
            birth_month=1,
            birth_year=-106,
            is_bc_era=True,
        )
        self.book_one = Book.objects.create(
            title="Идиот",
            genre="Роман",
            is_bc_era=False,
            publication_year=1868,
            author=self.author_one,
            amount=2,
        )
        self.book_two = Book.objects.create(
            title="О законах",
            genre="Философия",
            is_bc_era=True,
            publication_year=-54,
            author=self.author_two,
            amount=1,
        )
        self.book_three = Book.objects.create(
            title="Linux Format",
            genre="IT",
            is_bc_era=False,
            publication_year=1995,
            amount=200,
        )
        self.publication_one = Publication.objects.create(
            edition=2022,
            publisher="ЛИТ-Пресс",
            publication_place="С-Петербург",
            book=self.book_one,
            quantity=1,
        )
        self.issue_one = Issue.objects.create(
            book=self.book_three,
            issue_date=date(2026, 2, 15),
            volume_number=1,
            issue_number=1,
            quantity=4,
        )
        self.audiobook_one = Audiobook.objects.create(
            book=self.book_two, narrator="Машков, В.", duration=timedelta(hours=1, minutes=35, seconds=13)
        )

        self.client: APIClient = APIClient()

    def test_author_create_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:author_create")
        data = {
            "first_name": "Test_name",
            "surname": "Test_surname",
            "middle_name": "Test_middle",
            "birth_day": 12,
            "birth_month": 12,
            "birth_year": 1999,
            "is_bc_era": False,
        }
        response = self.client.post(url, data)
        author_data = Author.objects.get(birth_day=12, first_name="Test_name")
        serialized_author = AuthorSerializer(author_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), serialized_author.data)

    def test_author_list_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:author_list")
        response: DRFResponse = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        authors_data = Author.objects.all()
        serialized_authors = AuthorSerializer(authors_data, many=True)

        page_size = response.data.get("page_size", 2)
        expected_count = min(len(serialized_authors.data), page_size)
        self.assertEqual(len(response.data["results"]), expected_count)

    def test_author_retrieve_user(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("library:author_retrieve", args=(self.author_one.pk,))
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("first_name"), self.author_one.first_name)

    def test_author_update_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:author_update", args=(self.author_one.pk,))
        data = {
            "first_name": "Фёдор",
            "middle_name": "Михайловичъ",
        }

        response = self.client.patch(url, data)
        author_data = response.json()
        self.author_one.refresh_from_db()
        serialized_author = AuthorSerializer(self.author_one)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(author_data.get("first_name"), serialized_author.data.get("first_name"))

    def test_author_delete_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:author_destroy", args=(self.author_one.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Author.objects.filter(first_name=self.author_one.first_name).exists())

    def test_book_create_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:book_create")
        data = {
            "title": "Test_title",
            "genre": "философия",
            "is_bc_era": False,
            "publication_year": 1877,
            "author": self.author_one.pk,
            "amount": 2,
        }
        response = self.client.post(url, data)
        book_data = Book.objects.get(genre="философия", publication_year=1877)
        serialized_book = BookSerializer(book_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), serialized_book.data)

    def test_book_list_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:book_list")
        response: DRFResponse = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        books_data = Book.objects.all()
        serialized_books = BookSerializer(books_data, many=True)

        page_size = response.data.get("page_size", 2)
        expected_count = min(len(serialized_books.data), page_size)
        self.assertEqual(len(response.data["results"]), expected_count)

    def test_book_retrieve_moder(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("library:book_retrieve", args=(self.book_one.pk,))
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("genre"), self.book_one.genre)

    def test_book_update_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:book_update", args=(self.book_two.pk,))
        data = {
            "publication_year": 55,
            "is_bc_era": True,
            "amount": 2,
        }

        response = self.client.patch(url, data)
        book_data = response.json()
        self.book_two.refresh_from_db()
        serialized_book = BookSerializer(self.book_two)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(book_data.get("amount"), serialized_book.data.get("amount"))

    def test_book_delete_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:book_destroy", args=(self.book_two.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(title=self.book_two.title).exists())

    def test_publication_create_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:publication_create")
        data = {
            "edition": 2023,
            "publisher": "Москва-ПРЕСС",
            "publication_place": "Москва",
            "book": self.book_two.pk,
            "quantity": 1,
        }
        response = self.client.post(url, data)
        publication_data = Publication.objects.get(publisher="Москва-ПРЕСС", edition=2023)
        serialized_publication = PublicationSerializer(publication_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), serialized_publication.data)

    def test_publication_list_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:publication_list")
        response: DRFResponse = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        publications_data = Publication.objects.all()
        serialized_publications = PublicationSerializer(publications_data, many=True)

        page_size = response.data.get("page_size", 2)
        expected_count = min(len(serialized_publications.data), page_size)
        self.assertEqual(len(response.data["results"]), expected_count)

    def test_publication_retrieve_moder(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("library:publication_retrieve", args=(self.publication_one.pk,))
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("publisher"), self.publication_one.publisher)

    def test_publication_update_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:publication_update", args=(self.publication_one.pk,))
        data = {
            "publisher": "ЭКСМО",
            "edition": 2020,
            "quantity": 2,
        }

        response = self.client.patch(url, data)
        publication_data = response.json()
        self.publication_one.refresh_from_db()
        serialized_publication = PublicationSerializer(self.publication_one)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(publication_data.get("quantity"), serialized_publication.data.get("quantity"))

    def test_publication_delete_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:publication_destroy", args=(self.publication_one.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Publication.objects.filter(publisher=self.publication_one.publisher).exists())

    def test_issue_create_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:issue-list")
        data = {
            "book": self.book_three.pk,
            "issue_date": date(2026, 1, 26),
            "volume_number": 1,
            "issue_number": 1,
            "quantity": 5,
        }
        response = self.client.post(url, data)
        issue_data = Issue.objects.get(book=self.book_three, issue_date=date(2026, 1, 26))
        serialized_issue = IssueSerializer(issue_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), serialized_issue.data)

    def test_issue_list_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:issue-list")
        response: DRFResponse = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        issue_data = Issue.objects.all()
        serialized_issues = IssueSerializer(issue_data, many=True)

        page_size = response.data.get("page_size", 2)
        expected_count = min(len(serialized_issues.data), page_size)
        self.assertEqual(len(response.data["results"]), expected_count)

    def test_issue_retrieve_user(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("library:issue-detail", args=(self.issue_one.pk,))
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("issue_date"), datetime.strftime(self.issue_one.issue_date, "%Y-%m-%d"))

    def test_issue_update_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:issue-detail", args=(self.issue_one.pk,))
        data = {
            "issue_date": date(2026, 2, 17),
            "quantity": 2,
        }

        response = self.client.patch(url, data)
        issue_data = response.json()
        self.issue_one.refresh_from_db()
        serialized_issue = IssueSerializer(self.issue_one)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(issue_data.get("quantity"), serialized_issue.data.get("quantity"))

    def test_issue_delete_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:issue-detail", args=(self.issue_one.pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Issue.objects.filter(id=self.issue_one.pk).exists())

    def test_audiobook_create_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:audiobook_create")
        data = {
            "book": self.book_one.pk,
            "narrator": "Безруков, С.",
            "duration": timedelta(hours=5, minutes=34, seconds=22),
        }
        response = self.client.post(url, data)
        audiobook_data = Audiobook.objects.get(book=self.book_one, narrator="Безруков, С.")
        serialized_audiobook = AudiobookSerializer(audiobook_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), serialized_audiobook.data)

    def test_audiobook_list_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:audiobook_list")
        response: DRFResponse = self.client.get(url, {"page": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        audiobooks_data = Audiobook.objects.all()
        serialized_audiobooks = AudiobookSerializer(audiobooks_data, many=True)

        page_size = response.data.get("page_size", 2)
        expected_count = min(len(serialized_audiobooks.data), page_size)
        self.assertEqual(len(response.data["results"]), expected_count)

    def test_audiobook_retrieve_user(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("library:audiobook_retrieve", args=(self.audiobook_one.pk,))
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("narrator"), self.audiobook_one.narrator)

    def test_audiobook_update_moder(self) -> None:
        self.client.force_authenticate(user=self.user_moder)
        url = reverse("library:audiobook_update", args=(self.audiobook_one.pk,))
        data = {
            "narrator": "Михалков, Н.",
        }

        response = self.client.patch(url, data)
        audiobook_data = response.json()
        self.audiobook_one.refresh_from_db()
        serialized_audiobook = AudiobookSerializer(self.audiobook_one)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(audiobook_data.get("narrator"), serialized_audiobook.data.get("narrator"))

    def test_books_search_user(self) -> None:
        self.client.force_authenticate(user=self.user)
        url = reverse("library:book_search")
        search_data = {"author": "достоевский", "genre": "роман"}
        response = self.client.get(url, search_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([book["id"] for book in response.data], [self.book_one.id])

    def tearDown(self) -> None:
        CustomUser.objects.get(username="user_test").delete()
        CustomUser.objects.get(username="owner_user").delete()
        CustomUser.objects.get(username="moder_user").delete()
        Author.objects.all().delete()
        Book.objects.all().delete()
