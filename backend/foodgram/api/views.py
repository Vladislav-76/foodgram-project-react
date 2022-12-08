from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from recipes.models import Recipe, Tag
from .filter import RecipeFilter
from .permissions import AuthorAdminOrReadOnly
from .serializers import (
    CustomUserSerializer, RecipeSerializer,
    TagSerializer
)
from .pagination import MyPagination


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Представление для эндпойнта /users/"""
    queryset = User.objects.all()
    permission_classes = (AuthorAdminOrReadOnly,)
    serializer_class = CustomUserSerializer
    pagination_class = MyPagination

    # def create(self, request):
    #     """Создание пользователя"""
    #     serializer = CustomUserPostSerializer(
    #         data=request.data
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """Представление для эндпойнта /users/me/"""
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)


# class CustomAuthToken(ObtainAuthToken):
#     '''Представление для эндпойнта /auth/token/login/'''
#     serializer_class = CustomAuthTokenSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({'token': token.key})


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    """Представление для эндпойнта /recipes/"""
    queryset = Recipe.objects.all()
    pagination_class = MyPagination
    permission_classes = (AuthorAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        # if self.action == 'create' or self.action == 'partial_update':
        #     return RecipesSerializerCreate
        return RecipeSerializer
