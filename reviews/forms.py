from django import forms

from users.models import CustomUser
from .models import Review, ReviewAssignment


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'file', 'recommendation']

    def __init__(self, *args, **kwargs):
        kwargs.pop('assignment', None)
        super().__init__(*args, **kwargs)

class ReviewAssignmentForm(forms.ModelForm):
    class Meta:
        model = ReviewAssignment
        fields = ['reviewer']

    def __init__(self, *args, **kwargs):
        article = kwargs.pop('article', None)
        super().__init__(*args, **kwargs)

        queryset = CustomUser.objects.filter(role='reviewer')

        if article is not None:
            assigned_reviewer_ids = article.review_assignments.filter(is_active=True).values_list('reviewer_id', flat=True)
            queryset = queryset.exclude(id__in=assigned_reviewer_ids)

        self.fields['reviewer'].queryset = queryset
        self.fields['reviewer'].label_from_instance = (
            lambda user: f'{user.first_name} {user.last_name}'.strip() or user.username
        )