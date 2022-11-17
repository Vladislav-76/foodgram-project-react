from django.contrib import admin
from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
    ShoppingCart, Tag
)


admin.site.register([
    Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
    ShoppingCart, Tag]
)
