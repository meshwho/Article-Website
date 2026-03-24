from django.urls import path
from .views import (
    article_detail,
    choose_book,
    create_article,
    delete_article,
    delete_article_version,
    edit_article,
    my_articles,
    upload_new_version,
)

urlpatterns = [
    path('my/', my_articles, name='my_articles'),
    path('choose-book/', choose_book, name='choose_book'),
    path('create/<int:book_id>/', create_article, name='create_article'),
    path('<int:article_id>/', article_detail, name='article_detail'),
    path('<int:article_id>/edit/', edit_article, name='edit_article'),
    path('<int:article_id>/upload-version/', upload_new_version, name='upload_new_version'),
    path('<int:article_id>/delete/', delete_article, name='delete_article'),
    path('versions/<int:version_id>/delete/', delete_article_version, name='delete_article_version'),
]