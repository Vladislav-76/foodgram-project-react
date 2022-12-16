from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientsViewSet, RecipesViewSet,
                    TagViewSet)


app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('users', CustomUserViewSet, 'users')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('recipes', RecipesViewSet, basename='recipes')
router_v1.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
