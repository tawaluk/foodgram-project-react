import re

from django.core.validators import ValidationError


def validate_name(value):
    if not value:
        raise ValidationError("Имя не может быть пустым")

    if not re.match(r'^[\w.@+-]+$', value):
        raise ValidationError("Некорректное имя")
    return value
