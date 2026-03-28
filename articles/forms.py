from django import forms
from django.db import models
from django.utils import timezone

from books.models import Book
from .models import Article, ArticleVersion


class ArticleCreateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'abstract']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        fixed_book = kwargs.pop('fixed_book', None)
        super().__init__(*args, **kwargs)

        if fixed_book is not None:
            self.book = fixed_book
        else:
            self.book = None


class ArticleEditForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'abstract']


class ArticleVersionForm(forms.ModelForm):
    class Meta:
        model = ArticleVersion
        fields = ['file', 'comment']

class FullArticleUploadForm(forms.ModelForm):
    class Meta:
        model = ArticleVersion
        fields = ['file', 'comment']