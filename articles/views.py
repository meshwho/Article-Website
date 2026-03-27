from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from books.models import Book
from notifications.models import Notification
from users.decorators import role_required
from users.models import CustomUser
from .forms import ArticleCreateForm, ArticleEditForm, ArticleVersionForm
from .models import Article, ArticleVersion, ArticleCoauthorInvite

from django.contrib import messages

from reviews.models import Review

def can_view_article(user, article):
    if user.is_superuser:
        return True
    if user.role == 'admin':
        return True
    if article.author_id == user.id:
        return True
    if article.coauthors.filter(id=user.id).exists():
        return True
    if article.review_assignments.filter(reviewer=user, is_active=True).exists():
        return True
    return False
@login_required
@role_required(['author'])
def my_articles(request):
    articles = Article.objects.filter(author=request.user).order_by('-created_at')
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    revision_articles = articles.filter(status=Article.STATUS_REVISION_REQUIRED)
    review_articles = articles.filter(status=Article.STATUS_UNDER_REVIEW)
    accepted_articles = articles.filter(status=Article.STATUS_ACCEPTED)
    other_articles = articles.exclude(
        status__in=[
            Article.STATUS_REVISION_REQUIRED,
            Article.STATUS_UNDER_REVIEW,
            Article.STATUS_ACCEPTED,
        ]
    )
    observed_articles = Article.objects.filter(coauthors=request.user).exclude(author=request.user).order_by(
        '-created_at')

    return render(
        request,
        'articles/my_articles.html',
        {
            'articles': articles,
            'observed_articles': observed_articles,
            'unread_count': unread_count,
            'revision_articles': revision_articles,
            'review_articles': review_articles,
            'accepted_articles': accepted_articles,
            'other_articles': other_articles,
            'total_articles_count': articles.count(),
            'revision_count': revision_articles.count(),
            'review_count': review_articles.count(),
            'accepted_count': accepted_articles.count(),
        }
    )


@login_required
@role_required(['author'])
def choose_book(request):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    search_query = request.GET.get('q', '').strip()
    selected_creator = request.GET.get('creator', '').strip()

    books = Book.objects.filter(
        submission_deadline__gte=timezone.now()
    ).filter(
        models.Q(submission_mode=Book.SUBMISSION_MODE_ALL) |
        models.Q(submission_mode=Book.SUBMISSION_MODE_INVITATION, allowed_authors=request.user)
    ).select_related('created_by').distinct().order_by('submission_deadline', 'title')

    if search_query:
        books = books.filter(title__icontains=search_query)

    if selected_creator:
        books = books.filter(created_by_id=selected_creator)

    open_books = books.filter(submission_mode=Book.SUBMISSION_MODE_ALL)
    invitation_books = books.filter(submission_mode=Book.SUBMISSION_MODE_INVITATION)

    creator_ids = books.values_list('created_by_id', flat=True).distinct()

    creator_users = CustomUser.objects.filter(id__in=creator_ids).order_by('first_name', 'last_name', 'username')

    creators = []
    for user in creator_users:
        full_name = f'{user.first_name} {user.last_name}'.strip()
        creators.append({
            'id': user.id,
            'name': full_name or user.username
        })

    return render(
        request,
        'articles/choose_book.html',
        {
            'unread_count': unread_count,
            'search_query': search_query,
            'selected_creator': selected_creator,
            'creators': creators,
            'open_books': open_books,
            'invitation_books': invitation_books,
        }
    )


@login_required
@role_required(['author'])
def create_article(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    is_allowed = (
        (book.submission_deadline and book.submission_deadline >= timezone.now()) and
        (
            book.submission_mode == Book.SUBMISSION_MODE_ALL or
            (book.submission_mode == Book.SUBMISSION_MODE_INVITATION and book.allowed_authors.filter(id=request.user.id).exists())
        )
    )

    if not is_allowed:
        return redirect('choose_book')

    if request.method == 'POST':
        form = ArticleCreateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.book = book
            article.status = Article.STATUS_SUBMITTED
            article.save()

            if article.file:
                ArticleVersion.objects.create(
                    article=article,
                    file=article.file,
                    version_number=1,
                    comment='Initial version',
                    uploaded_by=request.user
                )

            admins = CustomUser.objects.filter(role='admin')
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title='New article submitted',
                    message=f'A new article "{article.title}" was submitted by {article.author}.',
                    link=reverse('book_article_detail', args=[article.book.id, article.id])
                )

            return redirect('my_articles')
    else:
        form = ArticleCreateForm(user=request.user, fixed_book=book)

    return render(
        request,
        'articles/create_article.html',
        {
            'unread_count': unread_count,
            'form': form,
            'book': book,
        }
    )


@login_required
def article_detail(request, article_id):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    article = get_object_or_404(
        Article.objects.prefetch_related(
            'versions',
            'review_assignments__reviews',
            'coauthors',
            'coauthor_invites'
        ),
        id=article_id
    )

    if not can_view_article(request.user, article):
        return redirect('dashboard')

    can_upload_new_version = False
    can_edit_article = False
    can_manage_coauthors = False

    if article.author_id == request.user.id:
        can_edit_article = True
        can_manage_coauthors = True

        latest_version = article.versions.first()
        if latest_version:
            can_upload_new_version = Review.objects.filter(
                assignment__article=article,
                article_version=latest_version
            ).exists()

    active_invite = article.coauthor_invites.filter(is_active=True).first()

    return render(
        request,
        'articles/article_detail.html',
        {
            'article': article,
            'unread_count': unread_count,
            'can_upload_new_version': can_upload_new_version,
            'can_edit_article': can_edit_article,
            'can_manage_coauthors': can_manage_coauthors,
            'active_invite': active_invite,
        }
    )


@login_required
@role_required(['author'])
def edit_article(request, article_id):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    article = get_object_or_404(
        Article,
        id=article_id,
        author=request.user
    )

    if request.method == 'POST':
        form = ArticleEditForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.save()
            return redirect('article_detail', article_id=article.id)
    else:
        form = ArticleEditForm(instance=article)

    return render(
        request,
        'articles/edit_article.html',
        {
            'unread_count': unread_count,
            'form': form,
            'article': article,
        }
    )


@login_required
@role_required(['author'])
def upload_new_version(request, article_id):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    article = get_object_or_404(
        Article.objects.prefetch_related('versions', 'review_assignments__reviews'),
        id=article_id,
        author=request.user
    )

    latest_version = article.versions.first()

    if latest_version is None:
        return redirect('article_detail', article_id=article.id)

    latest_version_has_review = Review.objects.filter(
        assignment__article=article,
        article_version=latest_version
    ).exists()

    if not latest_version_has_review:
        return redirect('article_detail', article_id=article.id)

    if request.method == 'POST':
        form = ArticleVersionForm(request.POST, request.FILES)
        if form.is_valid():
            next_version_number = latest_version.version_number + 1

            version = form.save(commit=False)
            version.article = article
            version.version_number = next_version_number
            version.uploaded_by = request.user
            version.save()

            article.file = version.file
            article.status = Article.STATUS_UNDER_REVIEW
            article.save()

            for assignment in article.review_assignments.filter(is_active=True):
                Notification.objects.create(
                    user=assignment.reviewer,
                    title='New article version uploaded',
                    message=f'A new version of the article "{article.title}" has been uploaded.',
                    link=f'/reviews/assignment/{assignment.id}/'
                )

            return redirect('article_detail', article_id=article.id)
    else:
        form = ArticleVersionForm()

    return render(
        request,
        'articles/upload_new_version.html',
        {
            'article': article,
            'form': form,
            'unread_count': unread_count,
        }
    )


@login_required
@role_required(['author'])
def create_coauthor_invite(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id,
        author=request.user
    )

    ArticleCoauthorInvite.objects.filter(
        article=article,
        is_active=True
    ).update(is_active=False)

    ArticleCoauthorInvite.objects.create(
        article=article,
        created_by=request.user
    )

    return redirect('article_detail', article_id=article.id)


def accept_coauthor_invite(request, token):
    invite = get_object_or_404(
        ArticleCoauthorInvite.objects.select_related('article'),
        token=token,
        is_active=True
    )

    article = invite.article

    if not request.user.is_authenticated:
        return render(
            request,
            'articles/coauthor_invite_landing.html',
            {
                'invite': invite,
                'article': article,
            }
        )

    if request.user.id == article.author_id:
        return redirect('article_detail', article_id=article.id)

    article.coauthors.add(request.user)

    messages.success(request, 'You have been added as a co-author.')
    return redirect('article_detail', article_id=article.id)

@login_required
@role_required(['author'])
def remove_coauthor(request, article_id, user_id):
    article = get_object_or_404(
        Article.objects.prefetch_related('coauthors'),
        id=article_id,
        author=request.user
    )

    if request.method == 'POST':
        article.coauthors.remove(user_id)
        return redirect('article_detail', article_id=article.id)

    return redirect('article_detail', article_id=article.id)
