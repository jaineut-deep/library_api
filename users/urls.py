from django.urls import path
from .apps import UsersConfig
from rest_framework.routers import DefaultRouter
from .views import (
    CustomUserListAPIView,
    CustomUserCreateAPIView,
    CustomUserRetrieveAPIView,
    CustomUserUpdateAPIView,
    CustomUserDestroyAPIView,
    LendingBookViewSet,
)

app_name = UsersConfig.name
router = DefaultRouter()
router.register(r"lending", LendingBookViewSet, basename="lending")


urlpatterns = [
    path("user/", CustomUserListAPIView.as_view(), name="user_list"),
    path("user/create/", CustomUserCreateAPIView.as_view(), name="user_create"),
    path("user/<int:pk>/", CustomUserRetrieveAPIView.as_view(), name="user_retrieve"),
    path("user/update/<int:pk>/", CustomUserUpdateAPIView.as_view(), name="user_update"),
    path("user/delete/<int:pk>/", CustomUserDestroyAPIView.as_view(), name="user_destroy"),
]
