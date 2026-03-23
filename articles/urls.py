from django.urls import path
from .views import (
    article_detail,
    create_article,
    edit_article,
    my_articles,
    upload_new_version,
)

urlpatterns = [
    path('my/', my_articles, name='my_articles'),
    path('create/', create_article, name='create_article'),
    path('<int:article_id>/', article_detail, name='article_detail'),
    path('<int:article_id>/edit/', edit_article, name='edit_article'),
    path('<int:article_id>/upload-version/', upload_new_version, name='upload_new_version'),
]