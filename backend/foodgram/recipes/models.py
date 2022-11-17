from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True, blank=False)
    color = models.CharField(max_length=7, unique=True, blank=False)
    slug = models.SlugField(max_length=200, unique=True, blank=False)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['id']

    def __str__(self):
        return self.name[:15]


class Ingredient(models.Model):
    name = models.CharField(max_length=200, blank=False)
    measurement_unit = models.CharField(
        max_length=200, blank=False
    )

    class Meta:
        unique_together = ('name', 'measurement_unit')
        verbose_name = "Игредиент"
        verbose_name_plural = "Игредиенты"
        ordering = ['id']

    def __str__(self):
        return self.name[:30]


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    name = models.SlugField(max_length=200, unique=True, blank=False)
    image = models.ImageField(
        upload_to='recipes/images/', null=True, default=None
    )
    text = models.TextField(help_text='Текст рецепта')
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(
            1, message='Время не может быть меньше 1'), ]
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ['id']
        unique_together = ('author', 'name')

    def __str__(self):
        return self.text[:15]


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Рецепт-Тег"
        verbose_name_plural = "Рецепты-Теги"
        ordering = ['id']

    def __str__(self):
        return f'{self.recipe}-{self.tag}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(
        validators=[
            MinValueValidator(0.1, message='Количество слишком мало'), ]
    )

    class Meta:
        verbose_name = "Рецепт-Игредиент"
        verbose_name_plural = "Рецепты-Игредиенты"
        ordering = ['id']

    def __str__(self):
        return f'{self.recipe}-{self.ingredient}'


class Favorite(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Список избранного"
        verbose_name_plural = "Списки избранного"
        ordering = ['id']

    def __str__(self):
        return f'{self.user_id}-{self.recipe_id}'


class ShoppingCart(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        ordering = ['id']

    def __str__(self):
        return f'{self.user_id}-{self.recipe_id}'
