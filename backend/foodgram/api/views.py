from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models import Avg, F, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST)
from recipes.models import Recipe, RecipeIngredient, Tag
from .filter import RecipeFilter
from .permissions import AuthorAdminOrReadOnly
from .serializers import (
    CustomUserSerializer, AddDelRecipeSerializer, RecipeSerializer,
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
    serializer_class = RecipeSerializer
    pagination_class = MyPagination
    permission_classes = (AuthorAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    # def get_serializer_class(self):
    #     # if self.action == 'create' or self.action == 'partial_update':
    #     #     return RecipesSerializerCreate
    #     return RecipeSerializer

    @action(
        methods=('get',), detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачать файл со списком покупок."""
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(amount=Sum('amount'))

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок для:\n\n{user.first_name}\n\n'
            f'{datetime.now().strftime("%d/%m/%Y %H:%M")}\n\n'
        )
        for ing in ingredients:
            shopping_list += (
                f'{ing["ingredient__name"]}: ' +
                f'{ing["amount"]}'
                f'{ing["ingredient__measurement_unit"]}\n'
            )
        shopping_list += '\n\n--------------------------------------------'
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(
        methods=('post', 'delete'), detail=True,
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated, AuthorAdminOrReadOnly]
    )
    def shopping_cart(self, request, pk):
        """Добавляет/удалет рецепт из списка покупок."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = AddDelRecipeSerializer(recipe)
        recipe_in_cart = user.carts.filter(id=recipe.id).exists()
        if request.method == 'POST':
            if not recipe_in_cart:
                user.carts.add(recipe)
                return Response(serializer.data, status=HTTP_201_CREATED)
            else:
                error = {'errors': 'Такой рецепт уже есть в списке.'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if recipe_in_cart:
                user.carts.remove(recipe)
                return Response(status=HTTP_204_NO_CONTENT)
            else:
                error = {'errors': 'Такого рецепта в списке нет.'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=('post', 'delete'), detail=True,
        url_path='favorite',
        permission_classes=[IsAuthenticated, AuthorAdminOrReadOnly]
    )
    def favorite(self, request, pk):
        """Добавляет/удалет рецепт в избранное."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = AddDelRecipeSerializer(recipe)
        recipe_in_favorite = user.favorites.filter(id=recipe.id).exists()
        if request.method == 'POST':
            if not recipe_in_favorite:
                user.favorites.add(recipe)
                return Response(serializer.data, status=HTTP_201_CREATED)
            else:
                error = {'errors': 'Такой рецепт уже есть в избранном.'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if recipe_in_favorite:
                user.favorites.remove(recipe)
                return Response(status=HTTP_204_NO_CONTENT)
            else:
                error = {'errors': 'Такого рецепта в избранном нет.'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
