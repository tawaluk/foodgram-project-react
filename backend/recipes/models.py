from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class Tag(models.Model):
    """Модель тегов"""
    name = models.CharField(
        verbose_name='имя тега',
        max_length=200,
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
    name = models.CharField(
        verbose_name='игридиент',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='единицы измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_for_ingredient"
            ),
            models.CheckConstraint(
                check=Q(name__length__gt=0),
                name="%(app_label)s_%(class)s_name_is_empty"
            ),
            models.CheckConstraint(
                check=Q(measurement_unit__length__gt=0),
                name="%(app_label)s_%(class)s_measurement_unit_is_empty"
            ),
        )

    def __str__(self) -> str:
        return f"{self.name} {self.measurement_unit}"

    def clean(self) -> None:
        """Очистка полей перед сохранением."""
        self.name = self.name.lower()
        self.measurement_unit = self.measurement_unit.lower()
        super().clean()


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
        max_length=4000,
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
