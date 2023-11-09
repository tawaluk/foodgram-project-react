from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, User22


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'bio', 'age',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'bio', 'age',)


class Users2(UserCreationForm):
    class Meta(UserCreationForm):
        model = User22
        fields = ('username', 'email', 'test')


class Userss2(UserChangeForm):
    class Meta(UserChangeForm):
        fields = ('username', 'email', 'test')
