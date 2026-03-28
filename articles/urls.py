from django.urls import path
from .views import (
    accept_coauthor_invite,
    article_detail,
    choose_book,
    create_article,
    create_coauthor_invite,
    edit_article,
    my_articles,
    remove_coauthor,
    upload_full_article,
    upload_new_version,
)

urlpatterns = [
    path('my/', my_articles, name='my_articles'),
    path('choose-book/', choose_book, name='choose_book'),
    path('create/<int:book_id>/', create_article, name='create_article'),
    path('<int:article_id>/', article_detail, name='article_detail'),
    path('<int:article_id>/edit/', edit_article, name='edit_article'),
path('<int:article_id>/upload-full-article/', upload_full_article, name='upload_full_article'),
    path('<int:article_id>/upload-version/', upload_new_version, name='upload_new_version'),
    path('<int:article_id>/coauthors/invite/', create_coauthor_invite, name='create_coauthor_invite'),
    path('<int:article_id>/coauthors/remove/<int:user_id>/', remove_coauthor, name='remove_coauthor'),
    path('coauthor-invite/<uuid:token>/', accept_coauthor_invite, name='accept_coauthor_invite'),
]