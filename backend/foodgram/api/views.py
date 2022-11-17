from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.serializers import UserSerializer
from .pagination import MyPagination


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Представление для эндпойнта /users/"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = MyPagination
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('$username',)
    # permission_classes = [AdminOrSUOnly]
    # lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """Представление для эндпойнта /users/me/"""
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
