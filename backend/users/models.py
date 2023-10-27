from django.contrib.auth.models import AbstractUser
from django.db.models import CheckConstraint, Q
from django.db import models
from ..core.validators import validate_alphabet, validate_only_letters


class FoodgramUser(AbstractUser):
    """Кастомная модель юзера"""
    email = models.EmailField(
        verbose_name="Электронная почта",
        max_length=256,
        unique=True,
        help_text="Максимум 256 символов",
    )
    username = models.CharField(
        verbose_name="Логин",
        max_length=150,
        unique=True,
        help_text="Максимум 150 символа, минимум 3",
        validators=[validate_alphabet, validate_only_letters],
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=150,
        help_text="Максимум 150 символа",
        validators=[validate_alphabet, validate_only_letters],
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150,
        help_text="Максимум 150 символа",
        validators=[validate_alphabet, validate_only_letters],
    )
    password = models.CharField(
        verbose_name="Пароль",
        max_length=150,
        help_text="Максимум 150 символов",
    )
    is_active = models.BooleanField(
        verbose_name="Активирован",
        default=True,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)
        constraints = (
            CheckConstraint(
                check=Q(username__length__gte=3),
                name="\nминимальная длина логина - 3 символа\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.username}: {self.email}"


class Subscriptions(models.Model):
    """Модель подписки"""
    author = models.ForeignKey(
        verbose_name="Автор рецепта",
        related_name="subscribers",
        to=FoodgramUser,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        verbose_name="Подписчики",
        related_name="subscriptions",
        to=FoodgramUser,
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name="Дата подписки",
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = (
            models.UniqueConstraint(
                fields=("author", "user"),
                name="\nRepeat subscription\n",
            ),
            CheckConstraint(
                check=~Q(author=models.F("user")), name="\nНельзя подписаться на самого себя\n"
            ),
        )

    def __str__(self) -> str:
        return f"{self.user.username} -> {self.author.username}"
