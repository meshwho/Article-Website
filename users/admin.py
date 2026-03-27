from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        ('Additional information', {
            'fields': (
                'role',
                'title',
                'orcid',
                'institution',
                'institution_address',
                'google_scholar',
                'citizenship',
            ),
        }),
    )

    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'role',
        'institution',
        'citizenship',
        'is_staff',
    )

    list_filter = (
        'role',
        'is_staff',
        'is_superuser',
        'is_active',
    )