from django.db import models
from users.models import UserFoodgram

from .validators import (MinValueAmountIngridient,
                         MinValueTimeCookingValidator, color_hex_validator)


class Ingredient(models.Model):
    """Модель рецепта."""

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="Название ингредиента",
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Единицы измерения"
    )

    class Meta:
        """Метамодель для модели Ingridient."""
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ["-name", ]

    def __str__(self) -> str:
        return f"{self.name}, {self.measurement_unit}"


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        verbose_name="название тега",
        help_text="введите имя тега",
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name="цвет тега",
        help_text="введите цвет тега в HEX-формате",
        max_length=7,
        unique=True,
        default="#ffffff",
        validators=[color_hex_validator]
    )
    slug = models.CharField(
        verbose_name="slug тега",
        help_text="slug имя тега",
        max_length=200,
        unique=True,
    )

    class Meta:
        """Метамодель для модели Tag."""

        verbose_name = "Тэг"
        verbose_name_plural = "Теги"
        ordering = ["-name", ]

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        UserFoodgram,
        verbose_name="автор рецепта",
        related_name="recipes",
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name="название рецепта",
        help_text="введите название рецепта",
        max_length=200,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
    )
    image = models.ImageField(
        verbose_name="фотография рецепта",
        help_text="добавьте изображение готового блюда",
        upload_to="recipes/",
        blank=True
    )
    text = models.TextField(
        verbose_name="текст рецепта",
        help_text="введите текст рецепта",
        max_length=5000,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientInRecipe",
        related_name="recipes",
        verbose_name="ингредиенты"
    )
    created = models.DateTimeField(
        verbose_name="Дата публикации рецепта",
        auto_now_add=True,
        db_index=True,
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="время приговления по рецепту в минутах",
        help_text="введите время приговления по рецепту в минутах",
        default=1,
        validators=[MinValueTimeCookingValidator(
            limit_value=1
        )],
    )

    class Meta:
        """Метамодель для модели Recipe."""

        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-created", ]

    def __str__(self) -> str:
        return self.name


class ShopCart(models.Model):
    """Модель списка покупок.
    Many-to-Many Recipe and UserFoodgram."""

    user = models.ForeignKey(
        UserFoodgram,
        verbose_name="покупатель",
        related_name="shop_carts_users",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="shopping_cart",
        related_name="shopping_cart",
        on_delete=models.CASCADE
    )

    class Meta:
        """Метамодель для модели ShopCart."""

        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="%(app_label)s_%(class)s_recipe_is_cart_already"
            ),
        ]

    def __str__(self):
        """Метод строкового представления модели."""
        return f"{self.user} {self.recipe}"


class Favorites(models.Model):
    """Модель списка избранных рецептов.
    Many-to-Many Recipe and UserFoodgram."""

    user = models.ForeignKey(
        UserFoodgram,
        verbose_name="пользователь",
        related_name="favorited",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="рецепт",
        related_name="favorited",
        on_delete=models.CASCADE
    )

    class Meta:
        """Метамодель Favorites."""

        verbose_name = "нравится"
        verbose_name_plural = "нравится"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class IngredientInRecipe(models.Model):
    """Модель колличества ингридиентов в рецептах.
        Many-to-Many Ingredient and Recipe."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="рецепт",
        related_name="ingridients_recipe",

    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="ингредиент",
        related_name="ingridient_recipe",

    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="количество",
        default=1,
        validators=[MinValueAmountIngridient(
            limit_value=1
        ), ]
    )

    class Meta:
        """Метамодель для модели IngredientInRecipe."""

        verbose_name = "ингредиент в рецепте"
        verbose_name_plural = "ингредиенты в рецептах"
        ordering = ("-recipe",)
        constraints = (
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="%(app_label)s_%(class)s_ingredient_already_added"
            ),
        )

    def __str__(self):
        return f"{self.ingredient} {self.recipe}"


class TagInRecipe(models.Model):
    """Создание модели тегов рецепта."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name="Теги",
        help_text="Выберите теги рецепта"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        help_text="Выберите рецепт")

    class Meta:
        """Мета-параметры модели."""

        verbose_name = "Тег рецепта"
        verbose_name_plural = "Теги рецепта"
        constraints = [
            models.UniqueConstraint(
                fields=["tag", "recipe"],
                name="unique_tag_in_recipe"
            )
        ]

    def __str__(self):
        """Метод строкового представления модели."""

        return f"{self.tag} {self.recipe}"
