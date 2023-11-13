from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import validate_name


class UserFoodgram(AbstractUser):
    """Модель фудграм юзера."""

    email = models.EmailField(
        max_length=254,
        help_text="введите е-mail",
        verbose_name="электронная почта",
        unique=True
    )
    username = models.CharField(
        max_length=150,
        verbose_name="имя пользователя",
        help_text="введите Ваш псевдоним",
        unique=True,
        db_index=True,
        validators=[validate_name]
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя",
        help_text="введите Ваше имя",
        validators=[validate_name]
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
        help_text="введите Вашу фамилию",
        validators=[validate_name]
    )
    password = models.CharField(
        verbose_name=_("Пароль"),
        max_length=150,
        help_text="Максимум 128 символов",
    )

    class Meta:
        """Метамодель для модели UserFoodgram."""

        ordering = ["username"]
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.username


class Fallow(models.Model):
    """Модель взаимодействия юзеров."""

    author = models.ForeignKey(
        UserFoodgram,
        related_name="follow",
        verbose_name="автор рецепта",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        UserFoodgram,
        related_name="follower",
        verbose_name="подписчик",
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name="дата подписки",
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        """Метамодель модели Fallow."""

        verbose_name = "подписка"
        verbose_name_plural = "подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_follow",
                violation_error_message="ошибка подписки",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user.username} -> {self.author.username}"
