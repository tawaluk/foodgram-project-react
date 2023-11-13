from django.contrib.admin import ModelAdmin, TabularInline, register
from django.utils.translation import gettext_lazy as _

from .models import (Favorites, Ingredient, IngredientInRecipe, Recipe,
                     ShopCart, Tag, TagInRecipe)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    """Настройка полей модели Ingredient в админке"""
    list_display = ('pk', 'name', 'measurement_unit',)
    search_fields = ('name',)


@register(Tag)
class TagAdmin(ModelAdmin):
    """Настройка полей модели Tag в админке"""
    list_display = ('pk', 'name', 'color', 'slug',)


class RecipeIngredientsInline(TabularInline):
    model = IngredientInRecipe
    min_num = 1
    extra = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    """Настройка полей модели Recipe в админке"""
    list_display = ('pk', 'author', 'name', 'favorited',)
    list_filter = ('author', 'name', 'tags')
    search_fields = ('author', 'name', 'tags')
    inlines = (RecipeIngredientsInline,)
    readonly_fields = ('favorited',)

    def favorited(self, obj):
        return obj.favorited.all().count()

    favorited.short_description = _('Количество добавлений в избранное')


@register(ShopCart)
class ShopCartAdmin(ModelAdmin):
    """Настройка полей модели ShopCart в админке"""
    list_display = ('pk', 'user', 'recipe')
    list_filter = ('user', 'recipe')


@register(Favorites)
class FavoriteAdmin(ModelAdmin):
    """Настройка полей модели Favorites в админке"""
    list_display = ('pk', 'user', 'recipe')
    list_filter = ('user', 'recipe')


@register(IngredientInRecipe)
class IngredientInRecipeAdmin(ModelAdmin):
    """Настройка полей модели IngredientInRecipe
    в админке.
    Админ может редактировать ингридиенты в рецептах."""

    list_display = ('pk', 'ingredient', 'recipe', 'amount',)
    list_filter = ('ingredient', 'recipe',)


@register(TagInRecipe)
class TagInRecipeAdmin(ModelAdmin):
    """Настройка полей модели TagInRecipe
        в админке.
        Админ может редактировать теги в рецептах.
        """
    list_display = ('pk', 'tag', 'recipe')
