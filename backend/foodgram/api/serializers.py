from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
# from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework.serializers import (
    ModelSerializer, SerializerMethodField, ValidationError)
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscriptions

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор для эндпойнта /users/"""
    password = serializers.CharField(
        min_length=4, write_only=True, required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password')
        # extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj):
        """Проверка подписки"""
        if self.context == {}:
            return False
        user = self.context['request'].user
        return (
            not user.is_anonymous
            and Subscriptions.objects.filter(user=user, author=obj).exists()
        )

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        try:
            user.set_password(validated_data['password'])
            user.save()
        except KeyError:
            pass
        return user


# class CustomUserPostSerializer(UserSerializer):
#     """Сериализатор для эндпойнта /users/"""

#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name', 'last_name')


# class CustomAuthTokenSerializer(serializers.Serializer):
#     '''Сериализатор для эндпойнта /auth/token/login/'''
#     password = serializers.CharField(
#         label="Password", style={'input_type': 'password'}
#     )
#     email = serializers.EmailField(label="Email")

#     def validate(self, attrs):
#         password = attrs.get('password')
#         email = attrs.get('email')

#         if email and password:
#             username = get_object_or_404(User, email=email).username
#             user = authenticate(username=username, password=password)
#             if user:
#                 if not user.is_active:
#                     msg = 'Аккаунт пользователя отключен.'
#                     raise serializers.ValidationError(
#                         msg, code='authorization'
#                     )
#             else:
#                 msg = 'Неверные почта или пароль.'
#                 raise serializers.ValidationError(msg, code='authorization')
#         else:
#             msg = 'Запрос должен включать "email" и "password".'
#             raise serializers.ValidationError(msg, code='authorization')

#         attrs['user'] = user
#         return attrs


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


# class RecipeIngredientSerialiser(serializers.ModelSerializer):
#     """Сериализатор ингредиентов для рецепта с количеством."""
#     id = IngredientSerializer()
#     name = serializers.CharField(required=False)
#     measurement_unit = serializers.CharField(required=False)
#     quantity = serializers.FloatField()

#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'name', 'measurement_unit', 'quantity')

#     def to_representation(self, instance):
#         data = IngredientSerializer(instance).data
#         data['quantity'] = instance.recipes
#         return data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('author', 'tags',)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.favorite.filter(author=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.shopping_cart.filter(author=user).exists()
        return False

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingredients
