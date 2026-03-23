from django.conf import settings
from django.db import models

from books.models import Book


class Article(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_SUBMITTED = 'submitted'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_REVISION_REQUIRED = 'revision_required'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_UNDER_REVIEW, 'Under review'),
        (STATUS_REVISION_REQUIRED, 'Revision required'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    title = models.CharField(
        max_length=255,
        verbose_name='Title'
    )

    abstract = models.TextField(
        blank=True,
        verbose_name='Abstract'
    )

    file = models.FileField(
        upload_to='articles/',
        blank=True,
        null=True,
        verbose_name='Article file'
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name='Book'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name='Author'
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name='Status'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at'
    )

    def __str__(self):
        return self.title


class ArticleVersion(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='Article'
    )

    file = models.FileField(
        upload_to='article_versions/',
        verbose_name='Version file'
    )

    version_number = models.PositiveIntegerField(
        verbose_name='Version number'
    )

    comment = models.TextField(
        blank=True,
        verbose_name='Author comment'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Uploaded at'
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_article_versions',
        verbose_name='Uploaded by'
    )

    class Meta:
        ordering = ['-version_number']
        unique_together = ('article', 'version_number')

    def __str__(self):
        return f'{self.article.title} - version {self.version_number}'