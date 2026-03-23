from django.conf import settings
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='User'
    )

    title = models.CharField(
        max_length=255,
        verbose_name='Title'
    )

    message = models.TextField(
        verbose_name='Message'
    )

    link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Link'
    )

    is_read = models.BooleanField(
        default=False,
        verbose_name='Read'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.title}'