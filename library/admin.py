from django.contrib import admin

from .models import Audiobook, Author, Book, Issue, Publication


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "surname", "birth_year", "is_bc_era")
    search_fields = ("first_name", "surname")
    list_filter = ("is_bc_era",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "is_bc_era", "publication_year", "author")
    search_fields = ("title",)
    list_filter = ("author",)


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("edition", "publisher", "book")
    search_fields = ("publisher",)
    list_filter = ("publisher",)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("issue_number", "issue_date", "book")
    search_fields = ("book",)
    list_filter = ("issue_date",)


@admin.register(Audiobook)
class AudiobookAdmin(admin.ModelAdmin):
    list_display = ("narrator", "duration", "book")
    search_fields = ("narrator",)
    list_filter = ("duration",)
