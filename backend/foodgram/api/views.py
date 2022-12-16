from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from users.models import Subscriptions

from .filter import RecipeFilter
from .pagination import MyPagination
from .permissions import AuthorAdminOrReadOnly
from .serializers import (AddDelRecipeSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeSerializer,
                          SubscriptionsSerializer, TagSerializer)


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Представление для эндпойнта /users/"""
    queryset = User.objects.all()
    permission_classes = (AuthorAdminOrReadOnly,)
    serializer_class = CustomUserSerializer
    pagination_class = MyPagination

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """Представление для эндпойнта /users/me/"""
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False, methods=['get'],
        permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Представление для списка подписок."""
        pages = self.paginate_queryset(
            Subscriptions.objects.filter(user=request.user))
        serializer = SubscriptionsSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=['post', 'delete'],
        url_path='subscribe', permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        """Представление для изменения подписки."""
        user = get_object_or_404(User, id=id)
        follow = Subscriptions.objects.filter(user=request.user, author=user)
        if request.method == 'POST':
            if user == request.user:
                error = {'errors': 'Нельзя подписаться на самого себя.'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            obj, created = Subscriptions.objects.get_or_create(
                user=request.user, author=user)
            if not created:
                error = {'errors': 'Вы уже подписаны на этого автора.'}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionsSerializer(
                obj, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not follow.exists():
            error = {'errors': 'Вы не подписаны на этого автора.'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Представление для эндпойнта /recipes/"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = MyPagination
    permission_classes = (AuthorAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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
        ).order_by('ingredient__name').annotate(quantity=Sum('amount'))

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок для:\n\n{user.first_name}\n\n'
            f'{datetime.now().strftime("%d/%m/%Y %H:%M")}\n\n'
        )
        for ing in ingredients:
            shopping_list += (
                f'{ing["ingredient__name"]}: '
                f'{ing["quantity"]}'
                f'{ing["ingredient__measurement_unit"]}\n'
            )
        shopping_list += '\n\n--------------------------------------------'
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    def field_manager(self, request, pk, field):
        """Добавляет/удаляет связи рецептов со списком покупок и избранным."""
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = AddDelRecipeSerializer(recipe)
        recipe_in_list = field.filter(id=recipe.id).exists()
        if request.method == 'POST':
            if not recipe_in_list:
                field.add(recipe)
                return Response(serializer.data, status=HTTP_201_CREATED)
            error = {'errors': 'Такой рецепт уже есть в списке.'}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        if recipe_in_list:
            field.remove(recipe)
            return Response(status=HTTP_204_NO_CONTENT)
        error = {'errors': 'Такого рецепта в списке нет.'}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=('post', 'delete'), detail=True,
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated, AuthorAdminOrReadOnly]
    )
    def shopping_cart(self, request, pk):
        """Добавляет/удалет рецепт из списка покупок."""
        return self.field_manager(request, pk, request.user.carts)

    @action(
        methods=('post', 'delete'), detail=True,
        url_path='favorite',
        permission_classes=[IsAuthenticated, AuthorAdminOrReadOnly]
    )
    def favorite(self, request, pk):
        """Добавляет/удалет рецепт в избранное."""
        return self.field_manager(request, pk, request.user.favorites)


class IngredientsViewSet(
    ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet
):
    """Представление для ингредиентов."""
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
