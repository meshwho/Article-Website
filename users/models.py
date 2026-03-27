from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_AUTHOR = 'author'
    ROLE_REVIEWER = 'reviewer'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_AUTHOR, 'Author'),
        (ROLE_REVIEWER, 'Reviewer'),
    ]

    title = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Title'
    )

    orcid = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='ORCID'
    )

    institution = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Institution'
    )

    institution_address = models.TextField(
        blank=True,
        verbose_name='Institution address'
    )

    google_scholar = models.URLField(
        blank=True,
        verbose_name='Google Scholar'
    )

    citizenship = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Citizenship'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_AUTHOR,
        verbose_name='Role'
    )

    def get_display_name(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.username

    def __str__(self):
        return self.get_display_name()