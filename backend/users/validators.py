import re

from django.core.validators import ValidationError


def validate_name(value):
    # Проверяем, что значение не пустое
    if not value:
        raise ValidationError('Имя не может быть пустым')

    # Проверяем, что значение соответствует условию
    if not re.match(r'^[\w.@+-]+$', value):
        raise ValidationError('Некорректное имя')

    # Если все проверки пройдены успешно, возвращаем значение
    return value
