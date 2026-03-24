from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from articles.models import Article
from users.decorators import role_required
from .forms import ReviewAssignmentForm, ReviewForm
from .models import Review, ReviewAssignment
from notifications.models import Notification


@login_required
@role_required(['reviewer'])
def reviewer_assignments(request):
    assignments = ReviewAssignment.objects.filter(
        reviewer=request.user
    ).select_related(
        'article',
        'article__book',
        'article__author'
    ).prefetch_related(
        'article__versions',
        'reviews'
    ).order_by('-assigned_at')

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    waiting_for_review = []
    already_reviewed_latest = []

    for assignment in assignments:
        latest_version = assignment.article.versions.first()
        latest_reviewed_version = assignment.reviews.order_by('-created_at').first()

        assignment.latest_version = latest_version
        assignment.latest_reviewed_version = latest_reviewed_version

        if latest_version is None:
            waiting_for_review.append(assignment)
        elif latest_reviewed_version is None:
            waiting_for_review.append(assignment)
        elif latest_reviewed_version.article_version_id != latest_version.id:
            waiting_for_review.append(assignment)
        else:
            already_reviewed_latest.append(assignment)

    return render(
        request,
        'reviews/reviewer_assignments.html',
        {
            'assignments': assignments,
            'unread_count': unread_count,
            'waiting_for_review': waiting_for_review,
            'already_reviewed_latest': already_reviewed_latest,
            'total_assignments_count': assignments.count(),
            'waiting_count': len(waiting_for_review),
            'reviewed_count': len(already_reviewed_latest),
        }
    )

@login_required
@role_required(['reviewer'])
def reviewer_article_detail(request, assignment_id):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    assignment = get_object_or_404(
        ReviewAssignment.objects.select_related(
            'article',
            'article__book',
            'article__author'
        ).prefetch_related(
            'article__versions',
            'reviews'
        ),
        id=assignment_id,
        reviewer=request.user,
        is_active=True
    )

    form = ReviewForm(assignment=assignment)

    return render(
        request,
        'reviews/reviewer_article_detail.html',
        {
            'unread_count': unread_count,
            'assignment': assignment,
            'article': assignment.article,
            'form': form,
        }
    )


@login_required
@role_required(['reviewer'])
def submit_review(request, assignment_id):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    assignment = get_object_or_404(
        ReviewAssignment.objects.select_related('article'),
        id=assignment_id,
        reviewer=request.user,
        is_active=True
    )

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, assignment=assignment)
        if form.is_valid():
            selected_version = form.cleaned_data['article_version']

            existing_review = Review.objects.filter(
                assignment=assignment,
                article_version=selected_version
            ).exists()

            if existing_review:
                form.add_error(
                    'article_version',
                    'You have already submitted a review for this version.'
                )
            else:
                review = form.save(commit=False)
                review.assignment = assignment
                review.save()

                Notification.objects.create(
                    user=assignment.article.author,
                    title='New review received',
                    message=f'A new review was submitted for your article "{assignment.article.title}".',
                    link=f'/articles/{assignment.article.id}/'
                )

                assignment.status = ReviewAssignment.STATUS_REVIEW_SUBMITTED
                assignment.save()

                article = assignment.article
                if review.recommendation == Review.RECOMMENDATION_ACCEPT:
                    article.status = Article.STATUS_ACCEPTED
                elif review.recommendation == Review.RECOMMENDATION_REVISION:
                    article.status = Article.STATUS_REVISION_REQUIRED
                elif review.recommendation == Review.RECOMMENDATION_REJECT:
                    article.status = Article.STATUS_REJECTED
                article.save()

                return redirect('reviewer_article_detail', assignment_id=assignment.id)
    else:
        form = ReviewForm(assignment=assignment)

    return render(
        request,
        'reviews/submit_review.html',
        {
            'unread_count': unread_count,
            'assignment': assignment,
            'form': form
        }
    )


@login_required
@role_required(['admin'])
def admin_articles(request):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    articles = Article.objects.select_related('author', 'book').order_by('-created_at')

    return render(
        request,
        'reviews/admin_articles.html',
        {
            'articles': articles,
            'unread_count': unread_count,
        }
    )


@login_required
@role_required(['admin'])
def admin_article_detail(request, article_id):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    article = get_object_or_404(
        Article.objects.select_related('author', 'book').prefetch_related(
            'review_assignments__reviews',
            'versions'
        ),
        id=article_id
    )

    if request.method == 'POST':
        form = ReviewAssignmentForm(request.POST, article=article)
        if form.is_valid():
            reviewer = form.cleaned_data['reviewer']

            existing_assignment = ReviewAssignment.objects.filter(
                article=article,
                reviewer=reviewer
            ).first()

            if existing_assignment:
                if existing_assignment.is_active:
                    messages.error(request, 'This reviewer is already assigned to this article.')
                else:
                    existing_assignment.is_active = True
                    existing_assignment.status = ReviewAssignment.STATUS_ASSIGNED
                    existing_assignment.save()

                    Notification.objects.create(
                        user=existing_assignment.reviewer,
                        title='New review assignment',
                        message=f'You have been assigned to review the article "{article.title}".',
                        link=reverse('reviewer_article_detail', args=[existing_assignment.id])
                    )

                    if article.status == Article.STATUS_SUBMITTED:
                        article.status = Article.STATUS_UNDER_REVIEW
                        article.save()

                    messages.success(request, 'Reviewer assigned successfully.')
                    return redirect('admin_article_detail', article_id=article.id)
            else:
                assignment = form.save(commit=False)
                assignment.article = article
                assignment.is_active = True
                assignment.save()

                Notification.objects.create(
                    user=assignment.reviewer,
                    title='New review assignment',
                    message=f'You have been assigned to review the article "{article.title}".',
                    link=reverse('reviewer_article_detail', args=[assignment.id])
                )

                if article.status == Article.STATUS_SUBMITTED:
                    article.status = Article.STATUS_UNDER_REVIEW
                    article.save()

                messages.success(request, 'Reviewer assigned successfully.')
                return redirect('admin_article_detail', article_id=article.id)
    else:
        form = ReviewAssignmentForm(article=article)

    return render(
        request,
        'reviews/admin_article_detail.html',
        {
            'unread_count': unread_count,
            'article': article,
            'form': form,
        }
    )

@login_required
@role_required(['admin'])
def remove_reviewer(request, article_id, assignment_id):
    assignment = get_object_or_404(
        ReviewAssignment.objects.select_related('article'),
        id=assignment_id,
        article_id=article_id
    )

    article = assignment.article
    assignment.is_active = False
    assignment.save()

    if not article.review_assignments.filter(is_active=True).exists() and article.status == Article.STATUS_UNDER_REVIEW:
        article.status = Article.STATUS_SUBMITTED
        article.save()

    messages.success(request, 'Reviewer removed from active assignments. Review history was kept.')
    return redirect('admin_article_detail', article_id=article.id)


@login_required
@role_required(['admin'])
def remove_reviewer_from_book_article(request, book_id, article_id, assignment_id):
    assignment = get_object_or_404(
        ReviewAssignment.objects.select_related('article'),
        id=assignment_id,
        article_id=article_id
    )

    article = assignment.article
    assignment.is_active = False
    assignment.save()

    if not article.review_assignments.filter(is_active=True).exists() and article.status == Article.STATUS_UNDER_REVIEW:
        article.status = Article.STATUS_SUBMITTED
        article.save()

    messages.success(request, 'Reviewer removed from active assignments. Review history was kept.')
    return redirect('book_article_detail', book_id=book_id, article_id=article_id)