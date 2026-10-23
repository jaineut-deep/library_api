from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import IsAuthenticated
from typing import Any

from library.paginators import LibraryPaginator
from users.permissions import IsManager

from .filters import BookFilter
from .models import Author, Book, Publication, Issue, Audiobook
from .serializers import (AuthorSerializer, BookSerializer, PublicationSerializer, IssueSerializer,
                          IssueMemberSerializer, AudiobookSerializer)


class BookSearchListView(generics.ListAPIView):
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = BookFilter

    search_fields = ["title", "author__surname"]
    permission_classes = [IsAuthenticated]


class AuthorCreateAPIView(generics.CreateAPIView):
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated, IsManager]


class AuthorListAPIView(generics.ListAPIView):
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    queryset = Author.objects.all().order_by("id")
    pagination_class = LibraryPaginator


class AuthorRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    queryset = Author.objects.all()


class AuthorUpdateAPIView(generics.UpdateAPIView):
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = Author.objects.all()


class AuthorDestroyAPIView(generics.DestroyAPIView):
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = Author.objects.all()


class BookCreateAPIView(generics.CreateAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsManager]


class BookListAPIView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.all().order_by("id")
    pagination_class = LibraryPaginator


class BookRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.all()


class BookUpdateAPIView(generics.UpdateAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = Book.objects.all()


class BookDestroyAPIView(generics.DestroyAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = Book.objects.all()


class PublicationCreateAPIView(generics.CreateAPIView):
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated, IsManager]


class PublicationListAPIView(generics.ListAPIView):
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Publication.objects.all().order_by("id")
    pagination_class = LibraryPaginator


class PublicationRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Publication.objects.all()


class PublicationUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = Publication.objects.all()


class PublicationDestroyAPIView(generics.DestroyAPIView):
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = Publication.objects.all()


@extend_schema_view(
    list=extend_schema(
        summary="Получить список выпусков журналов",
        parameters=[...],
        responses=IssueSerializer,
    ),
    retrieve=extend_schema(
        summary="Получить экземпляр выпуска журнала",
    ),
    update=extend_schema(
        summary="Изменение существующего выпуска журнала",
    ),
    partial_update=extend_schema(
        summary="Частичное изменение данных о выпуске журнала",
    ),
    create=extend_schema(
        summary="Создание нового выпуска журнала",
    ),
    destroy=extend_schema(
        summary="Удаление существующего выпуска журнала",
    ),
)
class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    queryset = Issue.objects.all().order_by("id")
    pagination_class = LibraryPaginator

    def get_permissions(self) -> Any:
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsManager()]
        elif self.action in ("list", "retrieve"):
            return [IsAuthenticated]

        return super().get_permissions()

    def get_serializer_class(self) -> Any:
        user = self.request.user

        if user.is_staff:
            return IssueSerializer
        elif not user.is_staff:
            return IssueMemberSerializer

        return super().get_serializer_class()


class AudiobookCreateAPIView(generics.CreateAPIView):
    serializer_class = AudiobookSerializer
    permission_classes = [IsAuthenticated, IsManager]


class AudiobookListAPIView(generics.ListAPIView):
    serializer_class = AudiobookSerializer
    permission_classes = [IsAuthenticated]
    queryset = Audiobook.objects.all().order_by("id")
    pagination_class = LibraryPaginator


class AudiobookRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = AudiobookSerializer
    permission_classes = [IsAuthenticated]
    queryset = Audiobook.objects.all()


class AudiobookUpdateAPIView(generics.UpdateAPIView):
    serializer_class = AudiobookSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = Audiobook.objects.all()


class AudiobookDestroyAPIView(generics.DestroyAPIView):
    serializer_class = AudiobookSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = Audiobook.objects.all()
