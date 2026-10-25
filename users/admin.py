from django.contrib import admin

from .models import CustomUser, LendingBook


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "city")
    exclude = ("password",)


@admin.register(LendingBook)
class LendingBookAdmin(admin.ModelAdmin):
    list_display = ("count_renewal", "updated_at", "member")
    search_fields = ("count_renewal",)
    list_filter = ("updated_at",)
