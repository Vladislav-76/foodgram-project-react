from django_filters import FilterSet
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр для эндпойнта /recipes/"""
    author = filters.CharFilter(field_name='author__id',)
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug', to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(method='cart_filter')

    def favorited_filter(self, queryset, name, value):
        if value:
            return queryset.filter(favorite=self.request.user)
        return queryset

    def cart_filter(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_cart=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'favorite')


class IngredientFilter(SearchFilter):
    search_param = 'name'
