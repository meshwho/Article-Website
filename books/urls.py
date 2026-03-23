from django.urls import path

from .views import (
    admin_books,
    book_article_detail,
    book_detail,
    create_book,
    edit_book,
    manage_book_authors,
)

urlpatterns = [
    path('dashboard/books/', admin_books, name='admin_books'),
    path('dashboard/books/create/', create_book, name='create_book'),
    path('dashboard/books/<int:book_id>/', book_detail, name='book_detail'),
    path('dashboard/books/<int:book_id>/edit/', edit_book, name='edit_book'),
    path('dashboard/books/<int:book_id>/authors/', manage_book_authors, name='manage_book_authors'),
    path('dashboard/books/<int:book_id>/articles/<int:article_id>/', book_article_detail, name='book_article_detail'),
]