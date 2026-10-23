from django.urls import path
from rest_framework.routers import DefaultRouter

from .apps import LibraryConfig
from .views import (
    AuthorCreateAPIView,
    AuthorDestroyAPIView,
    AuthorListAPIView,
    AuthorRetrieveAPIView,
    AuthorUpdateAPIView,
    BookCreateAPIView,
    BookDestroyAPIView,
    BookListAPIView,
    BookRetrieveAPIView,
    BookSearchListView,
    BookUpdateAPIView,
    PublicationCreateAPIView,
    PublicationDestroyAPIView,
    PublicationListAPIView,
    PublicationRetrieveAPIView,
    PublicationUpdateAPIView,
    AudiobookCreateAPIView,
    AudiobookListAPIView,
    AudiobookRetrieveAPIView,
    AudiobookUpdateAPIView,
    AudiobookDestroyAPIView,
    IssueViewSet,
)

app_name = LibraryConfig.name

router = DefaultRouter()
router.register(r"issues", IssueViewSet, basename="issue")


urlpatterns = [
    path("author/create/", AuthorCreateAPIView.as_view(), name="author_create"),
    path("author/", AuthorListAPIView.as_view(), name="author_list"),
    path("author/<int:pk>/", AuthorRetrieveAPIView.as_view(), name="author_retrieve"),
    path("author/update/<int:pk>/", AuthorUpdateAPIView.as_view(), name="author_update"),
    path("author/delete/<int:pk>/", AuthorDestroyAPIView.as_view(), name="author_destroy"),
    path("book/create/", BookCreateAPIView.as_view(), name="book_create"),
    path("book/", BookListAPIView.as_view(), name="book_list"),
    path("book/<int:pk>/", BookRetrieveAPIView.as_view(), name="book_retrieve"),
    path("book/update/<int:pk>/", BookUpdateAPIView.as_view(), name="book_update"),
    path("book/delete/<int:pk>/", BookDestroyAPIView.as_view(), name="book_destroy"),
    path("publication/create/", PublicationCreateAPIView.as_view(), name="publication_create"),
    path("publication/", PublicationListAPIView.as_view(), name="publication_list"),
    path("publication/<int:pk>/", PublicationRetrieveAPIView.as_view(), name="publication_retrieve"),
    path("publication/update/<int:pk>/", PublicationUpdateAPIView.as_view(), name="publication_update"),
    path("publication/delete/<int:pk>/", PublicationDestroyAPIView.as_view(), name="publication_destroy"),
    path("books/", BookSearchListView.as_view(), name="book_search"),
]
