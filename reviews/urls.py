from django.urls import path
from .views import (
    admin_article_detail,
    admin_articles,
    remove_reviewer,
    remove_reviewer_from_book_article,
    reviewer_article_detail,
    reviewer_assignments,
    submit_review,
)

urlpatterns = [
    path('my/', reviewer_assignments, name='reviewer_assignments'),
    path('assignment/<int:assignment_id>/', reviewer_article_detail, name='reviewer_article_detail'),
    path('submit/<int:assignment_id>/', submit_review, name='submit_review'),

    path('admin/articles/', admin_articles, name='admin_articles'),
    path('admin/articles/<int:article_id>/', admin_article_detail, name='admin_article_detail'),
    path('admin/articles/<int:article_id>/remove-reviewer/<int:assignment_id>/', remove_reviewer, name='remove_reviewer'),

    path(
        'admin/books/<int:book_id>/articles/<int:article_id>/remove-reviewer/<int:assignment_id>/',
        remove_reviewer_from_book_article,
        name='remove_reviewer_from_book_article'
    ),
]