from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class CustomUserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        (CustomUser.ROLE_AUTHOR, 'Author'),
        (CustomUser.ROLE_REVIEWER, 'Reviewer'),
    ]

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2']


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email']