from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import AbstractUser

from .forms import CustomUserCreationForm, CustomUserChangeForm, Users2, Userss2
from .models import CustomUser, User22


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', 'bio', 'age',]


class User2(AbstractUser):
    add_form = Users2
    form = Userss2
    model = User22
    ist_display = ['email', 'username', 'test']



admin.site.register(CustomUser, CustomUserAdmin)