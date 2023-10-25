from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Resipes(models.Model):
    """Moдель рецепта"""
    author = models.ForeignKey(
        User,
        verbose_name='автор рецепта',
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True
    )
    name = models.CharField(
        verbose_name='название блюда',
        max_length='200',
    )
    image = models.ImageField(
        verbose_name='изображение блюда',
        upload_to='recipe_images/',
    )
    text = models.TextField(
        verbose_name='описание блюда',
        max_length='4000',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='AmountIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления в минутах',
        default=0,
    )


class Tag(models.Model):
    """Модель тегов"""
    name = models.CharField(
        verbose_name='имя тега',
        max_length='200',
        validators=[NameTagsValidator],
        unique=True,
    )
    color = models.CharField(
        verbose_name='цвет тега в HEX',
        max_length=7,
        validators=[HexColorValidator],
        unique=True,
    )
    slug = models.CharField(
        verbose_name="Слаг тэга",
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} (цвет: {self.color})"


class Ingredient(models.Model):
    """Модель ингредиентов"""
