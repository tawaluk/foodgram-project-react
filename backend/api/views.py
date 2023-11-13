from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import Favorites, Ingredient, Recipe, ShopCart, Tag
from users.models import Fallow, UserFoodgram

from .filters import IngredientFilter, RecipeFilter
from .paginators import CustomPagination
from .permissions import SAFE_METHODS, AuthorOrStaffOrReadOnly
from .serializers import (FallowFoodgramSerializer, IngredientSerializer,
                          ReadRecipeSerializer, ReadUserFoodgramSerializer,
                          RecipeShortSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, TagSerializer)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вью дял тегов.
    Через АПИ требуются только GET запросы."""

    queryset = Tag.objects.all()
    permission_classes = [AllowAny]
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюха дял Ingredient.
    Через АПИ требуются только GET запросы."""

    queryset = Ingredient.objects.all()
    permission_classes = [AllowAny]
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели рецепта."""

    queryset = Recipe.objects.all()
    permission_classes = [AuthorOrStaffOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Роутинг сериализаторов исходя из действий."""

        if self.action in (SAFE_METHODS or ["retrieve", "list"]):
            return ReadRecipeSerializer
        return RecipeWriteSerializer

    def partial_update(self, request, *args, **kwargs):
        """Явно переопределяю. Нужно для тестов."""

        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {"error": "Вы не являетесь автором этого рецепта."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(
            instance, data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def favorite(self, request, pk):
        """Выбор метода для списка избранного."""
        if request.method == "POST":
            return self.add_to_target(Favorites, request.user, pk)
        return self.delete_from_target(Favorites, request.user, pk)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def shopping_cart(self, request, pk):
        """Выбор метода для списка покупок."""
        if request.method == "POST":
            return self.add_to_target(ShopCart, request.user, pk)
        return self.delete_from_target(ShopCart, request.user, pk)

    @staticmethod
    def add_to_target(model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({"errors": "Рецепт уже добавлен!"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response(
                data={"errors": "Рецепт не существует!"},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_from_target(model, user, pk):
        try:
            Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response(
                data={"errors": "Рецепт не существует!"},
                status=status.HTTP_404_NOT_FOUND
            )
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"errors": "Рецепт не существует!"},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCartSerializer()
        get_shopping_cart = shopping_cart.download_shopping_cart(request.user)
        return get_shopping_cart


class CustomUserViewSet(UserViewSet):
    """Вьюсет для кастомной модели пользователя."""

    queryset = UserFoodgram.objects.all()
    serializer_class = ReadUserFoodgramSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [AllowAny]

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        """Подписка и отписка от автора."""
        user = request.user
        author_id = self.kwargs.get("id")
        author = get_object_or_404(UserFoodgram, id=author_id)

        if request.method == "POST":
            serializer = FallowFoodgramSerializer(
                author,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Fallow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            subscription = Fallow.objects.filter(
                user=user,
                author=author
            )
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"errors": "Такой подписки не существует!"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Просмотр подписок на авторов."""
        user = request.user
        queryset = UserFoodgram.objects.filter(follow__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FallowFoodgramSerializer(pages,
                                              many=True,
                                              context={"request": request})
        return self.get_paginated_response(serializer.data)
