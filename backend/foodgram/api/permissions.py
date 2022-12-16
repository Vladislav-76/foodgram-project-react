from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, SAFE_METHODS)
from users.models import ADMIN


class AuthorAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    """Запись только автором или администратором."""
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.role == ADMIN
        ):
            return True
        return request.user == obj.author
