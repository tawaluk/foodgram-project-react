from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientsViewSet, RecipeViewSet,
                    TagsViewSet)

app_name = 'api'

router = DefaultRouter()

router.register(prefix='tags', viewset=TagsViewSet)
router.register(prefix='users', viewset=CustomUserViewSet)
router.register(prefix='recipes', viewset=RecipeViewSet)
router.register(prefix='ingredients', viewset=IngredientsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
