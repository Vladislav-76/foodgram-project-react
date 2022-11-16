from django.contrib import admin
from .models import (Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag)


admin.site.register([
    Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag])
