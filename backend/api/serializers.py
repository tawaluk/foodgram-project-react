import base64
import datetime

from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (ImageField, ModelSerializer,
                                        ReadOnlyField)

from recipes.models import (Ingredient, IngredientInRecipe, Recipe, ShopCart,
                            Tag)
from users.models import Fallow, UserFoodgram


class WriteUserFoodgramCreateSerializer(UserCreateSerializer):

    class Meta:
        model = UserFoodgram
        fields = ("email", "id", "username", "first_name",
                  "last_name", "password")


class ReadUserFoodgramSerializer(UserSerializer):
    """Чтение обьектов из модели через API."""

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = UserFoodgram
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, author):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Fallow.objects.filter(user=user, author=author).exists()

    def to_representation(self, instance):
        """Метод для представления сериализованных данных."""

        return super().to_representation(instance)


class Base64ImageField(ImageField):
    """Кодирование изображения в base64."""

    def to_internal_value(self, data):
        """Метод преобразования картинки."""

        if isinstance(data, str) and data.startswith("data:image"):
            format_value, imgstr = data.split(";base64,")
            ext = format_value.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="photo." + ext)

        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):
    """Сериализатор для получения тегов."""

    class Meta:
        model = Tag
        fields = (
            "id", "name", "color", "slug",
        )


class IngredientSerializer(ModelSerializer):
    """Сериализатор для получения ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientInRecipeWriteSerializer(ModelSerializer):

    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id", "amount",
        )


class ReadIngredientsInRecipeSerializer(ModelSerializer):
    """"Чтение обьектов из модели через API."""

    id = ReadOnlyField(read_only=True, source="ingredient.id")
    name = ReadOnlyField(read_only=True, source="ingredient.name")
    measurement_unit = ReadOnlyField(
        read_only=True,
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class ReadRecipeSerializer(ModelSerializer):
    """Чтение обьектов из модели через API."""

    tags = TagSerializer(many=True, read_only=True)
    author = ReadUserFoodgramSerializer(read_only=True)
    ingredients = ReadIngredientsInRecipeSerializer(
        many=True,
        read_only=True,
        source="ingridients_recipe"
    )
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, recipe):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.favorited.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return user.shop_carts_users.filter(recipe=recipe).exists()


class RecipeWriteSerializer(ModelSerializer):

    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()
    cooking_time = IntegerField()

    class Meta:
        model = Recipe

        fields = (
            "id",
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    # flake8: noqa: C901
    def validate(
            # flake8: noqa: C901
            self, obj):
        ingredients_list = []
        required_fields = ["name", "text", "cooking_time"]
        for field in required_fields:
            if not obj.get(field):
                raise ValidationError(f"{field} - Обязательное поле.")
        if not obj.get("tags"):
            raise ValidationError("Нужно указать минимум 1 тег.")
        if not obj.get("ingredients"):
            raise ValidationError("Нужно указать минимум 1 ингредиент.")

        ingredient_id_list = [item["id"] for item in obj.get("ingredients")]
        unique_ingredient_id_list = set(ingredient_id_list)

        if len(ingredient_id_list) != len(unique_ingredient_id_list):
            raise ValidationError("Ингредиенты должны быть уникальны.")
        for item in obj.get("ingredients"):
            ingredient_id = item["id"]
            ingredient_amount = int(item["amount"])
            try:
                ingredient = Ingredient.objects.get(id=ingredient_id)
            except Ingredient.DoesNotExist:
                raise ValidationError(
                    f"Ингредиент с id {ingredient_id} не существует!"
                )
            if ingredient in ingredients_list:
                raise ValidationError(
                    f"Ингредиент {ingredient} не должен повторяться!"
                )
            if ingredient_amount <= 0:
                raise ValidationError(
                    f"Ингредиента {ingredient} должно быть больше 0!"
                )
            ingredients_list.append(ingredient)
        return obj

    @staticmethod
    def validate_tags(value):
        if not value:
            raise ValidationError({
                "tags': 'Нужно выбрать хотя бы один тег!"
            })
        tags_set = set(value)
        if len(value) != len(tags_set):
            raise ValidationError({
                "tags": "Теги должны быть уникальными!"
            })
        return value

    @transaction.atomic
    def create_ingredients(self, ingredients, recipe):
        ingredient_ids = [element["id"] for element in ingredients]
        existing_ingredient_ids = set(ingredient_ids)
        if len(existing_ingredient_ids) != len(ingredient_ids):
            raise ValidationError("Некоторые ингредиенты не существуют!")
        ingredients_to_create = []
        for element in ingredients:
            ingredient_id = element["id"]
            amount = element["amount"]
            if ingredient_id not in existing_ingredient_ids:
                raise ValidationError(
                    f"Ингредиент с id {ingredient_id} не существует!"
                )
            ingredients_to_create.append(
                IngredientInRecipe(
                    ingredient_id=ingredient_id, recipe=recipe, amount=amount
                )
            )
        IngredientInRecipe.objects.bulk_create(ingredients_to_create)

    @staticmethod
    def create_tags(tags, recipe):
        """Метод добавления тега."""
        recipe.tags.set(tags)

    def create(self, validated_data):
        """Метод создания модели."""
        ingredients = validated_data.pop("ingredients")
        user = self.context.get("request").user
        tags = validated_data.pop("tags")

        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    @staticmethod
    def create_ingredients_amounts(ingredients, recipe):
        for ingredient in ingredients:
            ing, _ = IngredientInRecipe.objects.get_or_create(
                ingredient=get_object_or_404(
                    Ingredient.objects.filter(id=ingredient["id"])
                ),
                amount=ingredient["amount"],
            )
            recipe.ingredients.add(ing.id)

    @staticmethod
    def tags_and_ingredients_set(recipe, tags, ingredients):
        recipe.tags.set(tags)
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient["id"]),
                amount=ingredient["amount"]
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        """Если опять не так, то пажалуйста объясни,
        я отказался от избыточных запросов, но отказаться от
        строчек с тэгом и ингредиентом не могу,
         это не получается сделать/не знаю как."""
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        self.tags_and_ingredients_set(instance, tags, ingredients)
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context=self.context).data


class RecipeShortSerializer(ModelSerializer):
    """Вспомогательный сериализатор для необходимого вывода."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time"
        )


class SubscribeFoodgramSerializer(ReadUserFoodgramSerializer):

    recipes_count = IntegerField(
        source='recipe.count',
        read_only=True
    )
    recipes = SerializerMethodField()

    class Meta(ReadUserFoodgramSerializer.Meta):
        fields = ReadUserFoodgramSerializer.Meta.fields + (
            "recipes_count", "recipes"
        )
        read_only_fields = ("email", "username")

    def validate(self, data):
        author = self.instance
        user = self.context.get("request").user
        if Fallow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail="Вы уже подписаны на этого пользователя!",
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail="Нельзя подписаться на самого себя!",
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, author):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data


class FallowFoodgramSerializer(ReadUserFoodgramSerializer):

    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(ReadUserFoodgramSerializer.Meta):
        fields = ReadUserFoodgramSerializer.Meta.fields + (
            "recipes_count", "recipes"
        )
        read_only_fields = ("email", "username", "first_name", "last_name")

    def validate(self, data):
        writer = self.instance
        user = self.context.get("request").user
        if Fallow.objects.filter(author=writer, user=user).exists():
            raise ValidationError(
                detail="Вы уже подписаны на этого пользователя!",
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == writer:
            raise ValidationError(
                detail="Нельзя подписаться на самого себя!",
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    @staticmethod
    def get_recipes_count(author):
        return author.recipes.count()

    def get_recipes(self, author):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data


class ShoppingCartSerializer(ModelSerializer):

    class Meta:
        model = ShopCart
        fields = ("user", "recipe")

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
