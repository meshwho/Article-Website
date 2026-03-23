from django import forms
from django.db import models
from django.utils import timezone

from books.models import Book
from .models import Article, ArticleVersion


class ArticleCreateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'abstract', 'book', 'file']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        queryset = Book.objects.all()

        if user is not None:
            queryset = queryset.filter(submission_deadline__gte=timezone.now()).filter(
                models.Q(submission_mode=Book.SUBMISSION_MODE_ALL) |
                models.Q(submission_mode=Book.SUBMISSION_MODE_INVITATION, allowed_authors=user)
            ).distinct()

        self.fields['book'].queryset = queryset


class ArticleEditForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'abstract', 'file']


class ArticleVersionForm(forms.ModelForm):
    class Meta:
        model = ArticleVersion
        fields = ['file', 'comment']