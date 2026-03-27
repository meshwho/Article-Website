from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class CustomUserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        (CustomUser.ROLE_AUTHOR, 'Author'),
        (CustomUser.ROLE_REVIEWER, 'Reviewer'),
    ]

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=False)

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

    def __init__(self, *args, **kwargs):
        hide_role = kwargs.pop('hide_role', False)
        super().__init__(*args, **kwargs)

        if hide_role:
            self.fields['role'].widget = forms.HiddenInput()
            self.fields['role'].initial = CustomUser.ROLE_AUTHOR
        else:
            self.fields['role'].required = True

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role:
            return CustomUser.ROLE_AUTHOR
        return role


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