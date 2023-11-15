# Generated by Django 4.2.6 on 2023-11-15 13:45

from django.db import migrations, models
import django.db.models.deletion
import recipes.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorites',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'нравится',
                'verbose_name_plural': 'нравится',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200, verbose_name='Название ингредиента')),
                ('measurement_unit', models.CharField(max_length=200, verbose_name='Единицы измерения')),
            ],
            options={
                'verbose_name': 'Ингридиент',
                'verbose_name_plural': 'Ингридиенты',
                'ordering': ['-name'],
            },
        ),
        migrations.CreateModel(
            name='IngredientInRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(default=1, validators=[recipes.validators.MinValueAmountIngridient(limit_value=1)], verbose_name='количество')),
            ],
            options={
                'verbose_name': 'ингредиент в рецепте',
                'verbose_name_plural': 'ингредиенты в рецептах',
                'ordering': ('-recipe',),
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='введите название рецепта', max_length=200, verbose_name='название рецепта')),
                ('image', models.ImageField(blank=True, help_text='добавьте изображение готового блюда', upload_to='recipes/', verbose_name='фотография рецепта')),
                ('text', models.TextField(help_text='введите текст рецепта', max_length=5000, verbose_name='текст рецепта')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации рецепта')),
                ('cooking_time', models.PositiveIntegerField(default=1, help_text='введите время приговления по рецепту в минутах', validators=[recipes.validators.MinValueTimeCookingValidator(limit_value=1)], verbose_name='время приговления по рецепту в минутах')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='введите имя тега', max_length=200, unique=True, verbose_name='название тега')),
                ('color', models.CharField(default='#ffffff', help_text='введите цвет тега в HEX-формате', max_length=7, unique=True, validators=[recipes.validators.color_hex_validator], verbose_name='цвет тега')),
                ('slug', models.CharField(help_text='slug имя тега', max_length=200, unique=True, verbose_name='slug тега')),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Теги',
                'ordering': ['-name'],
            },
        ),
        migrations.CreateModel(
            name='TagInRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(help_text='Выберите рецепт', on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт')),
                ('tag', models.ForeignKey(help_text='Выберите теги рецепта', on_delete=django.db.models.deletion.CASCADE, to='recipes.tag', verbose_name='Теги')),
            ],
            options={
                'verbose_name': 'Тег рецепта',
                'verbose_name_plural': 'Теги рецепта',
            },
        ),
        migrations.CreateModel(
            name='ShopCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to='recipes.recipe', verbose_name='shopping_cart')),
            ],
            options={
                'verbose_name': 'Список покупок',
                'verbose_name_plural': 'Списки покупок',
            },
        ),
    ]
