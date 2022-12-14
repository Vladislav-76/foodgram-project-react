from django.contrib.auth.models import AbstractUser
from django.db import models


ROLES = (
    ('user', 'Юзер'),
    ('admin', 'Адинистратор'),
)


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True, blank=False
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='Email',
        unique=True, blank=False
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        blank=False
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        blank=False
    )
    role = models.CharField(max_length=20, choices=ROLES, default='user')

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['id']


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    def __str__(self):
        name = f'{self.user}-{self.author}'
        return name
