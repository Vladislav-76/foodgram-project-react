from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """ Модель тегов.
        Поле color в HEX.
    """
    name = models.CharField(
        verbose_name='Название', max_length=200,
        unique=True, db_index=True, blank=False,
        help_text='Название тега',
    )
    color = models.CharField(
        verbose_name='Цвет в HEX', max_length=7,
        validators=[RegexValidator(regex=r'^#([A-Fa-f0-9]{6})$')],
        blank=False,
    )
    slug = models.SlugField(max_length=200, unique=True, blank=False)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['name']

    def __str__(self):
        return self.name[:15]


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        verbose_name='Название ингредиента', max_length=200, blank=False
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения', max_length=200, blank=False
    )

    class Meta:
        unique_together = ('name', 'measurement_unit')
        verbose_name = "Игредиент"
        verbose_name_plural = "Игредиенты"
        ordering = ['name']

    def __str__(self):
        return self.name[:30]


class Recipe(models.Model):
    """Модель рецепта."""
    tags = models.ManyToManyField(
        Tag, verbose_name='Тег', related_name='recipes'
    )
    author = models.ForeignKey(
        User, verbose_name='Автор рецепта', on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиенты',
        related_name='recipes', through='RecipeIngredient'
    )
    favorite = models.ManyToManyField(
        User, verbose_name='Избранные рецепты',
        related_name='favorites',
    )
    shopping_cart = models.ManyToManyField(
        User, verbose_name='Список покупок',
        related_name='carts'
    )
    name = models.SlugField(
        verbose_name='Блюдо', max_length=200, unique=True, blank=False
    )
    image = models.ImageField(
        verbose_name='Картинка', upload_to='recipes/images/',
        null=True, default=None
    )
    text = models.TextField(
        verbose_name='Текст рецепта', help_text='Текст рецепта'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(
            1, message='Время не может быть меньше 1'), ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ['-pub_date']
        unique_together = ('author', 'name')

    def __str__(self):
        return self.text[:15]


# class RecipeTag(models.Model):
#     recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
#     tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

#     class Meta:
#         verbose_name = "Рецепт-Тег"
#         verbose_name_plural = "Рецепты-Теги"
#         ordering = ['id']

#     def __str__(self):
#         return f'{self.recipe}-{self.tag}'


class RecipeIngredient(models.Model):
    """Модель связи рецепты - ингредиенты."""
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепты',
        related_name='ingredient', on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='Ингредиенты',
        related_name='recipe', on_delete=models.CASCADE
    )
    quantity = models.FloatField(
        verbose_name='Количество', blank=False,
        validators=[
            MinValueValidator(0.1, message='Количество слишком мало'), ]
    )

    class Meta:
        verbose_name = "Рецепт-Игредиент"
        verbose_name_plural = "Рецепты-Игредиенты"
        ordering = ['recipe']
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f'{self.recipe}-{self.ingredient}'


# class Favorite(models.Model):
#     user_id = models.ForeignKey(User, on_delete=models.CASCADE)
#     recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)

#     class Meta:
#         verbose_name = "Список избранного"
#         verbose_name_plural = "Списки избранного"
#         ordering = ['id']

#     def __str__(self):
#         return f'{self.user_id}-{self.recipe_id}'


# class ShoppingCart(models.Model):
#     user_id = models.ForeignKey(User, on_delete=models.CASCADE)
#     recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)

#     class Meta:
#         verbose_name = "Список покупок"
#         verbose_name_plural = "Списки покупок"
#         ordering = ['id']

#     def __str__(self):
#         return f'{self.user_id}-{self.recipe_id}'
