# Generated by Django 2.2.19 on 2022-12-07 10:33

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название ингредиента')),
                ('measurement_unit', models.CharField(max_length=200, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Игредиент',
                'verbose_name_plural': 'Игредиенты',
                'ordering': ['name'],
                'unique_together': {('name', 'measurement_unit')},
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(max_length=200, unique=True, verbose_name='Блюдо')),
                ('image', models.ImageField(default=None, null=True, upload_to='recipes/images/', verbose_name='Картинка')),
                ('text', models.TextField(help_text='Текст рецепта', verbose_name='Текст рецепта')),
                ('cooking_time', models.IntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время не может быть меньше 1')], verbose_name='Время приготовления')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта')),
                ('favorite', models.ManyToManyField(related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Избранные рецепты')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Название тега', max_length=200, unique=True, verbose_name='Название')),
                ('color', models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(regex='^#([A-Fa-f0-9]{6})$')], verbose_name='Цвет в HEX')),
                ('slug', models.SlugField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField(validators=[django.core.validators.MinValueValidator(0.1, message='Количество слишком мало')], verbose_name='Количество')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to='recipes.Ingredient', verbose_name='Ингредиенты')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient', to='recipes.Recipe', verbose_name='Рецепты')),
            ],
            options={
                'verbose_name': 'Рецепт-Игредиент',
                'verbose_name_plural': 'Рецепты-Игредиенты',
                'ordering': ['recipe'],
                'unique_together': {('recipe', 'ingredient')},
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='recipes.RecipeIngredient', to='recipes.Ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='shopping_cart',
            field=models.ManyToManyField(related_name='carts', to=settings.AUTH_USER_MODEL, verbose_name='Список покупок'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipes.Tag', verbose_name='Тег'),
        ),
        migrations.AlterUniqueTogether(
            name='recipe',
            unique_together={('author', 'name')},
        ),
    ]
