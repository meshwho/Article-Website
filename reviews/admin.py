from django.contrib import admin
from .models import ReviewAssignment, Review


@admin.register(ReviewAssignment)
class ReviewAssignmentAdmin(admin.ModelAdmin):
    list_display = ('article', 'reviewer', 'status', 'assigned_at')
    list_filter = ('status', 'assigned_at')
    search_fields = ('article__title', 'reviewer__username', 'reviewer__first_name', 'reviewer__last_name')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'recommendation', 'created_at')
    list_filter = ('recommendation', 'created_at')
    search_fields = ('assignment__article__title', 'comment')