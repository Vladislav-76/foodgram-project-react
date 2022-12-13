from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    CustomUserViewSet, IngredientsViewSet, RecipesViewSet, TagViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users', CustomUserViewSet, 'users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
