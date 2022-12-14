from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Tag


admin.site.register([
    Ingredient, Recipe, RecipeIngredient, Tag]
)
