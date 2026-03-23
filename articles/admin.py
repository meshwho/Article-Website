from django.contrib import admin
from .models import Article, ArticleVersion


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'book',
        'author',
        'status',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'status',
        'book',
        'created_at',
    )

    search_fields = (
        'title',
        'abstract',
    )


@admin.register(ArticleVersion)
class ArticleVersionAdmin(admin.ModelAdmin):
    list_display = (
        'article',
        'version_number',
        'uploaded_by',
        'uploaded_at',
    )

    list_filter = (
        'uploaded_at',
    )

    search_fields = (
        'article__title',
        'comment',
    )