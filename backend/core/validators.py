from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def validate_alphabet(value):
    """Валидируем кириллицу и латинницу"""
    cyrillic_alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    latin_alphabet = "abcdefghijklmnopqrstuvwxyz"
    has_cyrillic = any(char in cyrillic_alphabet for char in value.lower())
    has_latin = any(char in latin_alphabet for char in value.lower())
    if has_cyrillic and has_latin:
        raise ValidationError('Имя может содержать символы только из одного алфавита')


def validate_only_letters(value):
    """Валидируем возможность писать только буквы"""
    type_value = RegexValidator(
        regex=r'^[a-zA-Zа-яА-Я\s]+$',
        message='используйте только буквы',
        code='invalid value',
    )
