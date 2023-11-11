from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug')
    is_favorited = filters.BooleanFilter(
        method='is_recipe_in_favorites_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_recipe_in_shoppingcart_filter')

    def is_recipe_in_favorites_filter(self, queryset, name, value):
        if value:
            user = self.request.user
            return queryset.filter(favorited__user_id=user.id)
        return queryset

    def is_recipe_in_shoppingcart_filter(self, queryset, name, value):
        if value:
            user = self.request.user
            return queryset.filter(shopping_cart__user_id=user.id)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')
