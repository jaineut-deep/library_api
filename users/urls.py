from django.urls import path
from rest_framework.routers import DefaultRouter

from .apps import UsersConfig
from .views import (
    CustomUserCreateAPIView,
    CustomUserDestroyAPIView,
    CustomUserListAPIView,
    CustomUserRetrieveAPIView,
    CustomUserUpdateAPIView,
    LendingBookViewSet,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = UsersConfig.name
router = DefaultRouter()
router.register(r"lendings", LendingBookViewSet, basename="lending")


urlpatterns = [
    path("user/", CustomUserListAPIView.as_view(), name="user_list"),
    path("user/create/", CustomUserCreateAPIView.as_view(), name="user_create"),
    path("user/<int:pk>/", CustomUserRetrieveAPIView.as_view(), name="user_retrieve"),
    path("user/update/<int:pk>/", CustomUserUpdateAPIView.as_view(), name="user_update"),
    path("user/delete/<int:pk>/", CustomUserDestroyAPIView.as_view(), name="user_destroy"),
    # token_routes
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
] + router.urls
