from rest_framework.permissions import BasePermission


class IsNotManager(BasePermission):
    def has_permission(self, request, view) -> bool:
        return not request.user.is_staff


class IsManager(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user.is_staff


class IsUserSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj
