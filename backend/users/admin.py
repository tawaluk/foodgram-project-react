from django.contrib import admin
from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import Group, UserAdmin

from .models import Fallow, UserFoodgram

admin.site.unregister(Group)  # Убираем видимость админки групп


@register(UserFoodgram)
class MyUserAdmin(UserAdmin):
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


@register(Fallow)
class FollowAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
