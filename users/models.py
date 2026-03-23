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

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_AUTHOR,
        verbose_name='Role'
    )

    def get_display_name(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        if full_name:
            return f'{full_name} ({self.username})'
        return self.username

    def __str__(self):
        return self.get_display_name()