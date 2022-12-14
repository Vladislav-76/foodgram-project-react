from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, SAFE_METHODS)


class AuthorAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    """Запись только автором или администратором."""
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or request.user.role == 'admin':
            return True
        return request.user == obj.author
