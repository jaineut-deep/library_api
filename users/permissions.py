from typing import Any

from rest_framework.permissions import BasePermission


class IsNotManager(BasePermission):
    def has_permission(self, request: Any, view: Any) -> bool:
        return not request.user.is_staff


class IsManager(BasePermission):
    def has_permission(self, request: Any, view: Any) -> Any:
        return request.user.is_staff


class IsUserSelf(BasePermission):
    def has_object_permission(self, request: Any, view: Any, obj: Any) -> Any:
        return request.user == obj
