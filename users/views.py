from typing import Any

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from library.paginators import LibraryPaginator
from users.tasks import send_update_lending_mail
from users.models import CustomUser, LendingBook
from users.permissions import IsManager, IsNotManager, IsUserSelf
from users.serializers import (
    CustomUserSerializer,
    LendingBookMemberSerializer,
    LendingBookSerializer,
    LendingBookStaffSerializer,
    RegisterSerializer,
)


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

    def get_permissions(self) -> Any:
        if self.action == "create":
            return [IsAuthenticated(), IsNotManager()]
        elif self.action == "destroy":
            return [IsAuthenticated(), IsManager()]
        elif self.action in ("list", "retrieve", "partial_update", "update"):
            return [IsAuthenticated()]

        return super().get_permissions()

    def get_serializer_class(self) -> Any:
        if self.action in (
            "create",
            "list",
            "retrieve",
            "destroy",
        ):
            return LendingBookSerializer
        elif self.action in ("partial_update", "update") and self.request.user.is_staff:
            return LendingBookStaffSerializer
        elif self.action in ("partial_update", "update") and not self.request.user.is_staff:
            return LendingBookMemberSerializer

        return super().get_serializer_class()

    def get_queryset(self) -> Any:
        user = self.request.user

        if self.action in ("list", "retrieve", "partial_update", "update") and user.is_staff:
            return LendingBook.objects.all().order_by("id")
        elif self.action in ("list", "retrieve", "partial_update", "update") and not user.is_staff:
            return LendingBook.objects.filter(member=user).order_by("id")
        elif self.action == "destroy":
            return LendingBook.objects.all()

        return super().get_queryset()

    def perform_create(self, serializer):
        instance = serializer.save()
        send_update_lending_mail.delay(
            instance.member.email, True, "create", instance.publication.book.title
        )

    def retrieve(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()

        if not request.user.is_staff:
            if instance.member_id != request.user.pk:
                raise PermissionDenied("Недостаточно прав для отображения объекта.")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer: Any) -> None:
        instance = serializer.instance
        user = self.request.user

        if not user.is_staff:
            if instance.member_id != user.pk:
                raise PermissionDenied("Недостаточно прав для обновления объекта.")
        updated_inst = serializer.save()
        procedure = ""
        if instance.count_renewal == updated_inst.count_renewal:
            if updated_inst.status is True and (updated_inst.status is not instance.status):
                procedure = "permit"
            elif updated_inst.status is False and (updated_inst.status is not instance.status):
                procedure = "deny"
            send_update_lending_mail.delay(
                updated_inst.member.email, False, procedure, updated_inst.publication.book.title
            )
        elif instance.count_renewal != updated_inst.count_renewal:
            serializer.save(status=None)
            procedure = "renewal"
            send_update_lending_mail.delay(
                updated_inst.member.email, False, procedure, updated_inst.publication.book.title
            )
