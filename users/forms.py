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
        fields = [
            'title',
            'first_name',
            'last_name',
            'username',
            'email',
            'role',
            'orcid',
            'institution',
            'institution_address',
            'google_scholar',
            'citizenship',
            'password1',
            'password2',
        ]


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = [
            'title',
            'first_name',
            'last_name',
            'username',
            'email',
            'orcid',
            'institution',
            'institution_address',
            'google_scholar',
            'citizenship',
        ]