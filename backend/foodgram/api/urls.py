from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, RecipesViewSet, TagViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', CustomUserViewSet, 'users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')

urlpatterns = [
    # path('auth/token/login/', CustomAuthToken.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
