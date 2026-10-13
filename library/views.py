from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from library.paginators import LibraryPaginator
from users.permissions import IsManager
from .serializers import AuthorSerializer, BookSerializer, PublicationSerializer
from .models import Author, Book, Publication


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
