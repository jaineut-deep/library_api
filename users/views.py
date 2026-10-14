from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from library.paginators import LibraryPaginator
from users.models import CustomUser, LendingBook
from users.permissions import IsNotManager, IsManager, IsUserSelf
from users.serializers import (CustomUserSerializer, RegisterSerializer, LendingBookSerializer,
                               LendingBookMemberSerializer, LendingBookStaffSerializer)


class CustomUserListAPIView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.filter(is_staff=False)
    permission_classes = [IsAuthenticated, IsManager]
    pagination_class = LibraryPaginator


class CustomUserCreateAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]


class CustomUserRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated, IsUserSelf]


class CustomUserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated, IsUserSelf]


class CustomUserDestroyAPIView(generics.DestroyAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated, IsManager]


@extend_schema_view(

    list=extend_schema(
        summary="Получить список выдач книг",
        parameters=[...],
        responses=LendingBookSerializer,
    ),
    retrieve=extend_schema(
        summary="Получить экземпляр выдачи книги",
    ),
    update=extend_schema(
        summary="Изменение существующего объекта выдачи",
    ),
    partial_update=extend_schema(
        summary="Частичное изменение данных о выдаче",
    ),
    create=extend_schema(
        summary="Создание новой выдачи книги",
    ),
    destroy=extend_schema(
        summary="Удаление существующей выдачи",
    ),
)
class LendingBookViewSet(viewsets.ModelViewSet):
    serializer_class = LendingBookSerializer
    queryset = LendingBook.objects.all()
    pagination_class = LibraryPaginator

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsNotManager()]
        elif self.action == "destroy":
            return [IsAuthenticated(), IsManager()]
        elif self.action in ("list", "retrieve", "partial_update", "update"):
            return [IsAuthenticated()]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ("create", "list", "retrieve", "destroy",):
            return LendingBookSerializer
        elif self.action in ("partial_update", "update") and self.request.user.is_staff:
            return LendingBookStaffSerializer
        elif self.action in ("partial_update", "update") and not self.request.user.is_staff:
            return LendingBookMemberSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user

        if self.action in ("list", "retrieve", "partial_update", "update") and user.is_staff:
            return LendingBook.objects.all().order_by("id")
        elif self.action in ("list", "retrieve", "partial_update", "update") and not user.is_staff:
            return LendingBook.objects.filter(member=user).order_by("id")
        elif self.action == "destroy":
            return LendingBook.objects.all()

        return super().get_queryset()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if not request.user.is_staff:
            if instance.member is not request.user:
                raise PermissionDenied("Недостаточно прав для отображения объекта.")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = serializer.instance
        user = self.request.user

        if not user.is_staff:
            if instance.member is not user:
                raise PermissionDenied("Недостаточно прав для обновления объекта.")
            serializer.save(status=None)
        serializer.save()
