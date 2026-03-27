from django import forms

from users.models import CustomUser
from .models import Book


class BookForm(forms.ModelForm):
    submission_deadline = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Book
        fields = ['title', 'description', 'submission_deadline']

class BookAuthorsForm(forms.ModelForm):
    allowed_authors = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='author'),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Book
        fields = ['allowed_authors']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['allowed_authors'].label_from_instance = (
            lambda user: f'{user.first_name} {user.last_name}'.strip() or user.username
        )