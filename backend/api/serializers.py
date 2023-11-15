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
    """Внес изменения в логику проверки существования id."""

    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id", "amount",
        )

    def validate_amount(self, value):
        if value < 1:
            raise ValidationError(
                "Количество ингредиента должно быть больше 1")
        return value


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
    ingredients = IngredientInRecipeWriteSerializer(many=True, required=True)
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

    def validate(self, attrs):
        if not attrs.get("ingredients"):
            raise ValidationError("Нельзя создать рецепт без ингредиентов")
        if not attrs.get("tags"):
            raise ValidationError("Нельзя создать рецепт без тегов")
        if attrs.get("cooking_time") and attrs["cooking_time"] <= 0:
            raise ValidationError("Время приготовления должно быть больше 0")
        return attrs

    def validate_ingredients(self, ingredients):
        ingredient_ids = set()
        for ingredient in ingredients:
            ingredient_id = ingredient["id"]
            if ingredient_id in ingredient_ids:
                raise ValidationError(f"Ингредиент {ingredient_id} уже существует")
            ingredient_ids.add(ingredient_id)
            if ingredient["amount"] <= 0:
                raise ValidationError(f"Количество ингредиента {ingredient_id} должно быть больше 0")
        return ingredients

    def validate_tags(self, tags):
        tag_ids = set()
        for tag in tags:
            tag_id = tag.id
            if tag_id in tag_ids:
                raise ValidationError(f"Тег {tag_id} уже существует")
            tag_ids.add(tag_id)
        return tags

    def create_ingredients(self, ingredients, recipe):
        ingredient_create = []
        for ingredient in ingredients:
            ingredient_obj = ingredient["id"]
            ingredient_id = ingredient_obj.id if isinstance(ingredient_obj, Ingredient) else ingredient_obj
            ingredient_amount = ingredient["amount"]
            ingredient_create.append(
                IngredientInRecipe(
                    ingredient_id=ingredient_id,
                    amount=ingredient_amount,
                    recipe=recipe
                )
            )
        IngredientInRecipe.objects.bulk_create(ingredient_create)

    def create(self, validated_data):
        """Метод создания модели."""
        ingredients = validated_data.pop("ingredients")
        user = self.context.get("request").user
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data, author=user)
        recipe.save()
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        instance.tags.clear()
        instance.tags.set(tags)
        self.create_ingredients(ingredients=ingredients, recipe=instance)
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
