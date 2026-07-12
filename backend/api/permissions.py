from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsOwnerRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "owner"


class IsAdvertiserRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "advertiser"
