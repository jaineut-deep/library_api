import django_filters

from .models import Book


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
    )
    genre = django_filters.CharFilter(
        field_name="genre",
        lookup_expr="iexact",
    )
    author = django_filters.CharFilter(
        field_name="author__surname",
        lookup_expr="icontains",
    )

    class Meta:
        model = Book
        fields = []
