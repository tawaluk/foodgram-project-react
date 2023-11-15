import datetime

from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import IngredientInRecipe


class ShoppingCartService:
    @staticmethod
    def download_shopping_cart(user):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            "ingredient__name",
            "ingredient__measurement_unit"
        ).annotate(amount=Sum("amount"))
        today = datetime.datetime.today()
        shopping_list = (
            f"Список покупок: {user.get_full_name()}\n\n"
            f"Дата: {today:%Y-%m-%d}\n\n"
        )
        shopping_list += '\n'.join([
            f"- {ingredient['ingredient__name']} "
            f"({ingredient['ingredient__measurement_unit']})"
            f" - {ingredient['amount']}"
            for ingredient in ingredients
        ])
        shopping_list += f"\n\nFoodgram ({today:%Y})"
        filename = f"{user.username}_shopping_list.txt"
        response = HttpResponse(
            shopping_list, content_type="text.txt; charset=utf-8"
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response
