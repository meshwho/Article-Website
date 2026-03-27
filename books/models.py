from django.conf import settings
from django.db import models

import uuid


class Book(models.Model):
    SUBMISSION_MODE_INVITATION = 'invitation'

    SUBMISSION_MODE_CHOICES = [
        (SUBMISSION_MODE_INVITATION, 'Only invited authors can submit'),
    ]

    title = models.CharField(
        max_length=255,
        verbose_name='Title'
    )

    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )

    submission_mode = models.CharField(
        max_length=20,
        choices=SUBMISSION_MODE_CHOICES,
        default=SUBMISSION_MODE_INVITATION,
        verbose_name='Submission mode'
    )

    submission_deadline = models.DateTimeField(
        verbose_name='Submission deadline',
        null = True,
        blank = True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name='Created by'
    )

    allowed_authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='allowed_books',
        verbose_name='Allowed authors'
    )

    def __str__(self):
        return self.title


class BookAuthorInvite(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='author_invites',
        verbose_name='Book'
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='Token'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_book_author_invites',
        verbose_name='Created by'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    def __str__(self):
        return f'Invite for {self.book.title}'