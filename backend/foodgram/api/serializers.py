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
    tags = TagSerializer(many=True, read_only=True)
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
        # favor = obj.favorite
        if user.is_authenticated:
            return user.favorites.filter(id=obj.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.carts.filter(id=obj.id).exists()
        return False

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingredients

    def validate(self, data):
        name = str(self.initial_data.get('name'))
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')

        if not name.replace(' ', '').isalpha():
            raise ValidationError('Название должно содержать буквы.')

        if not isinstance(tags, list) or not isinstance(ingredients, list):
            raise ValidationError('Теги и ингредиенты должны быть списками.')

        for tag in tags:
            result = Tag.objects.filter(id=tag)
            if not result:
                raise ValidationError(f'Такого тега {tag} нет.')

        ingredients_amount = []
        for ingredient in ingredients:
            result = Ingredient.objects.filter(id=ingredient['id'])
            if not result:
                raise ValidationError(f'Такого ингредиента {ingredient} нет.')
            amount = ingredient.get('amount')
            if not isinstance(amount, (int, float)):
                raise ValidationError(
                    f'Значение количества {amount} должно быть числом.')
            ingredient = get_object_or_404(Ingredient, id=ingredient['id'])
            ingredients_amount.append(
                {'ingredient': ingredient, 'amount': amount})

        data['name'] = name
        data['tags'] = tags
        data['ingredients'] = ingredients_amount
        data['author'] = self.context.get('request').user
        return data

    def create(self, validated_data):
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.get('ingredients')
        tags = validated_data.get('tags')
        recipe.image = validated_data.get('image', recipe.image)
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time)
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            for ingredient in ingredients:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount']
                )
        recipe.save()
        return recipe


class AddDelRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления/удаления рецепта."""

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe
