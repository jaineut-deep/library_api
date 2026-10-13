from rest_framework import generics
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


class LendingBookCreateAPIView(generics.CreateAPIView):
    serializer_class = LendingBookSerializer
    permission_classes = [IsAuthenticated, IsNotManager]


class LendingBookListAPIView(generics.ListAPIView):
    serializer_class = LendingBookSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LibraryPaginator

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return LendingBook.objects.all().order_by("id")
        return LendingBook.objects.filter(member=user).order_by("id")


class LendingBookRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LendingBookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return LendingBook.objects.all().order_by("id")
        return LendingBook.objects.filter(member=user).order_by("id")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if not request.user.is_staff:
            if instance.member is not request.user:
                raise PermissionDenied("Недостаточно прав для отображения объекта.")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class LendingBookUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LendingBookMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return LendingBookStaffSerializer
        return LendingBookMemberSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return LendingBook.objects.all().order_by("id")
        return LendingBook.objects.filter(member=user).order_by("id")

    def perform_update(self, serializer):
        instance = serializer.instance
        user = self.request.user

        if not user.is_staff:
            if instance.member is not user:
                raise PermissionDenied("Недостаточно прав для обновления объекта.")
            serializer.save(status=None)
        serializer.save()


class LendingBookDestroyAPIView(generics.DestroyAPIView):
    serializer_class = LendingBookSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = LendingBook.objects.all()
