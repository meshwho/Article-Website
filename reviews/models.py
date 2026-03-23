from django.conf import settings
from django.db import models

from articles.models import Article, ArticleVersion


class ReviewAssignment(models.Model):
    STATUS_ASSIGNED = 'assigned'
    STATUS_REVIEW_SUBMITTED = 'review_submitted'

    STATUS_CHOICES = [
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_REVIEW_SUBMITTED, 'Review submitted'),
    ]

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='review_assignments',
        verbose_name='Article'
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_assignments',
        verbose_name='Reviewer'
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_ASSIGNED,
        verbose_name='Assignment status'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Assigned at'
    )

    class Meta:
        verbose_name = 'Review assignment'
        verbose_name_plural = 'Review assignments'
        unique_together = ('article', 'reviewer')

    def __str__(self):
        return f'{self.article} -> {self.reviewer}'


class Review(models.Model):
    RECOMMENDATION_ACCEPT = 'accept'
    RECOMMENDATION_REVISION = 'revision'
    RECOMMENDATION_REJECT = 'reject'

    RECOMMENDATION_CHOICES = [
        (RECOMMENDATION_ACCEPT, 'Accept'),
        (RECOMMENDATION_REVISION, 'Revision required'),
        (RECOMMENDATION_REJECT, 'Reject'),
    ]

    assignment = models.ForeignKey(
        ReviewAssignment,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Assignment'
    )

    article_version = models.ForeignKey(
        ArticleVersion,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Article version',
        null=True,
        blank=True
    )

    comment = models.TextField(
        verbose_name='Comment'
    )

    file = models.FileField(
        upload_to='reviews/',
        blank=True,
        null=True,
        verbose_name='Review file'
    )

    recommendation = models.CharField(
        max_length=20,
        choices=RECOMMENDATION_CHOICES,
        verbose_name='Recommendation'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['assignment', 'article_version'],
                name='unique_review_per_assignment_and_version'
            )
        ]

    def __str__(self):
        if self.article_version:
            return f'Review for {self.assignment.article} (version {self.article_version.version_number})'
        return f'Review for {self.assignment.article}'