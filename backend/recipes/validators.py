from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


def color_hex_validator(value):
    """Валидатор коректности ввода цвета"""
    if not value.startswith('#'):
        raise ValidationError('цвет должен начинаться с символа #')
    if len(value) != 7:
        raise ValidationError('цвет должен состоять из 6 символов после #')
    try:
        int(value[1:], 16)
    except ValueError:
        raise ValidationError('некорректный формат цвета')


def min_long_name_validator(value):
    """Валидатор коректности длины имени"""
    if len(value) < 2:
        raise ValidationError('минимальная длина этого поля 2')


class MinValueTimeCookingValidator(MinValueValidator):
    """Валидатор корректности вводимого значения времени
     приготовления в рецепте"""
    message = 'не менее 1 минуты!'


class MinValueAmountIngridient(MinValueValidator):
    """Валидатор корректности вводимого значения
     колличества единиц ингридиентов в рецепте"""
    message = 'не менее 1 единицы/штуки'
