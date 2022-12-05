from rest_framework import serializers
# from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework.serializers import (
    ModelSerializer, SerializerMethodField, ValidationError)
from recipes.models import Tag
from users.models import Subscriptions

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор для эндпойнта /users/"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password')
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj):
        """Проверка подписки"""
        if self.context == {}:
            return False
        user = self.context['request'].user
        return Subscriptions.objects.filter(user=user, author=obj).exists()


# class CustomUserPostSerializer(UserSerializer):
#     """Сериализатор для эндпойнта /users/"""

#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name', 'last_name')


class CustomAuthTokenSerializer(serializers.Serializer):
    '''Сериализатор для эндпойнта /auth/token/login/'''
    password = serializers.CharField(
        label="Password", style={'input_type': 'password'}
    )
    email = serializers.EmailField(label="Email")

    def validate(self, attrs):
        password = attrs.get('password')
        email = attrs.get('email')

        if email and password:
            username = get_object_or_404(User, email=email).username
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    msg = 'Аккаунт пользователя отключен.'
                    raise serializers.ValidationError(
                        msg, code='authorization'
                    )
            else:
                msg = 'Неверные почта или пароль.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Запрос должен включать "email" и "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'
