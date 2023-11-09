import base64

from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (ImageField, ModelSerializer,
                                        ReadOnlyField)

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
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
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Fallow.objects.filter(user=user, author=author).exists()

    def to_representation(self, instance):
        """Метод для представления сериализованных данных"""

        user = self.context.get('request').user
        if user.is_authenticated and instance == user:
            return super().to_representation(instance)
        return super().to_representation(instance)


class Base64ImageField(ImageField):
    """Кодирование изображения в base64."""
    def to_internal_value(self, data):
        """Метод преобразования картинки"""
        if isinstance(data, str) and data.startswith('data:image'):
            format_value, imgstr = data.split(';base64,')
            ext = format_value.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):
    """Сериализатор для получения тегов."""

    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',
        )


class IngredientSerializer(ModelSerializer):
    """Сериализатор для получения ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeWriteSerializer(ModelSerializer):

    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id', 'amount',
        )


class ReadIngredientsInRecipeSerializer(ModelSerializer):
    """"Чтение обьектов из модели через API."""

    id = ReadOnlyField(read_only=True, source='ingredient.id')
    name = ReadOnlyField(read_only=True, source='ingredient.name')
    measurement_unit = ReadOnlyField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReadRecipeSerializer(ModelSerializer):
    """Чтение обьектов из модели через API."""
    tags = TagSerializer(many=True, read_only=True)
    author = ReadUserFoodgramSerializer(read_only=True)
    ingredients = ReadIngredientsInRecipeSerializer(
        many=True,
        read_only=True,
        source='ingridients_recipe'
    )
    image = Base64ImageField()
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorited.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shop_carts_users.filter(recipe=recipe).exists()


class RecipeWriteSerializer(ModelSerializer):
    """Модель моей боли"""
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()
    cooking_time = IntegerField()

    class Meta:
        model = Recipe

        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    @staticmethod
    def validate_ingredients(value):
        ingredients_list = []
        for item in value:
            try:
                ingredient = Ingredient.objects.get(id=item['id'])
            except ValidationError:
                raise ("Ингридиент не существует!")
            if ingredient in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Ингридиенты не должны повторяться!'
                })
            if int(item['amount']) <= 0:
                raise ValidationError({
                    'amount': 'Количество ингредиента должно быть не меньше 1!'
                })
            ingredients_list.append(ingredient)
        return value

    def validate(self, obj):
        for field in ['name', 'text', 'cooking_time']:
            if not obj.get(field):
                raise ValidationError(
                    f'{field} - Обязательное поле.'
                )
        if not obj.get('tags'):
            raise ValidationError(
                'Нужно указать минимум 1 тег.'
            )
        if not obj.get('ingredients'):
            raise ValidationError(
                'Нужно указать минимум 1 ингредиент.'
            )
        ingredient_id_list = [item['id'] for item in obj.get('ingredients')]
        unique_ingredient_id_list = set(ingredient_id_list)
        if len(ingredient_id_list) != len(unique_ingredient_id_list):
            raise ValidationError(
                'Ингредиенты должны быть уникальны.'
            )
        return obj

    @staticmethod
    def validate_tags(value):
        if not value:
            raise ValidationError({
                'tags': 'Нужно выбрать хотя бы один тег!'
            })
        tags_set = set(value)
        if len(value) != len(tags_set):
            raise ValidationError({
                'tags': 'Теги должны быть уникальными!'
            })
        return value

    @staticmethod
    def create_ingredients(ingredients, recipe):
        """Метод создания ингредиента"""
        for element in ingredients:
            id = element['id']
            ingredient = Ingredient.objects.get(pk=id)
            amount = element['amount']
            IngredientInRecipe.objects.create(
                ingredient=ingredient, recipe=recipe, amount=amount
            )

    @staticmethod
    def create_tags(tags, recipe):
        """Метод добавления тега"""
        recipe.tags.set(tags)

    def create(self, validated_data):
        """Метод создания модели"""
        # print(f'ВСЕ ДААНЫЕ {validated_data}')
        ingredients = validated_data.pop('ingredients')
        user = self.context.get('request').user
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    @staticmethod
    def create_ingredients_amounts(ingredients, recipe):
        for ingredient in ingredients:
            ing, _ = IngredientInRecipe.objects.get_or_create(
                ingredient=get_object_or_404(
                    Ingredient.objects.filter(id=ingredient['id'])
                ),
                amount=ingredient['amount'],
            )
            recipe.ingredients.add(ing.id)

    @transaction.atomic
    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        IngredientInRecipe.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        self.tags_and_ingredients_set(instance, tags, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance,
                                    context=self.context).data


class RecipeShortSerializer(ModelSerializer):
    """Вспомогательный сериализатор для необходимого вывода"""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeFoodgramSerializer(ReadUserFoodgramSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(ReadUserFoodgramSerializer.Meta):
        fields = ReadUserFoodgramSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Fallow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    @staticmethod
    def get_recipes_count(author):
        return author.recipes.count()

    def get_recipes(self, author):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
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
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        writer = self.instance
        user = self.context.get('request').user
        if Fallow.objects.filter(author=writer, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == writer:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    @staticmethod
    def get_recipes_count(author):
        return author.recipes.count()

    def get_recipes(self, author):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data
