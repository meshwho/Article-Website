from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from users.decorators import role_required
from .forms import BookAuthorsForm, BookForm
from .models import Book, BookAuthorInvite
from articles.models import Article

from django.contrib import messages
from reviews.forms import ReviewAssignmentForm
from reviews.models import ReviewAssignment

from django.urls import reverse
from notifications.models import Notification

from io import BytesIO
from pathlib import Path
import zipfile

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from django.utils import timezone

@login_required
@role_required(['admin'])
def admin_books(request):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    books = Book.objects.select_related('created_by').prefetch_related('allowed_authors').order_by('-created_at')

    return render(
        request,
        'books/admin_books.html',
        {
            'books': books,
            'unread_count': unread_count,
        }
    )


@login_required
@role_required(['admin'])
def create_book(request):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user
            book.submission_mode = Book.SUBMISSION_MODE_INVITATION
            book.save()
            return redirect('book_detail', book_id=book.id)
    else:
        form = BookForm()

    return render(
        request,
        'books/create_book.html',
        {
            'form': form,
            'unread_count': unread_count,
        }
    )


@login_required
@role_required(['admin'])
def book_detail(request, book_id):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    book = get_object_or_404(
        Book.objects.prefetch_related('allowed_authors'),
        id=book_id
    )

    articles = get_filtered_book_articles(book, request)

    selected_status = request.GET.get('status', '')
    selected_author = request.GET.get('author', '')
    selected_reviewer_filter = request.GET.get('reviewer_filter', '')

    if selected_status:
        articles = articles.filter(status=selected_status)

    if selected_author:
        articles = articles.filter(author_id=selected_author)

    if selected_reviewer_filter == 'with_reviewer':
        articles = articles.filter(review_assignments__isnull=False).distinct()
    elif selected_reviewer_filter == 'without_reviewer':
        articles = articles.filter(review_assignments__isnull=True)

    authors = book.articles.select_related('author').values_list(
        'author__id',
        'author__first_name',
        'author__last_name',
        'author__username'
    ).distinct()

    author_choices = []
    for author_id, first_name, last_name, username in authors:
        full_name = f'{first_name} {last_name}'.strip()
        author_choices.append({
            'id': author_id,
            'name': full_name or username
        })

    authors_form = BookAuthorsForm(instance=book)

    return render(
        request,
        'books/book_detail.html',
        {
            'book': book,
            'articles': articles,
            'authors_form': authors_form,
            'selected_status': selected_status,
            'selected_author': selected_author,
            'selected_reviewer_filter': selected_reviewer_filter,
            'author_choices': author_choices,
            'status_choices': book.articles.model.STATUS_CHOICES,
            'unread_count': unread_count,
        }
    )

@login_required
@role_required(['admin'])
def edit_book(request, book_id):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save(commit=False)
            book.submission_mode = Book.SUBMISSION_MODE_INVITATION
            book.save()
            return redirect('book_detail', book_id=book.id)
    else:
        form = BookForm(instance=book)

    return render(
        request,
        'books/edit_book.html',
        {
            'book': book,
            'form': form,
            'unread_count': unread_count,
        }
    )


@login_required
@role_required(['admin'])
def manage_book_authors(request, book_id):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    book = get_object_or_404(Book, id=book_id)
    search_query = request.GET.get('q', '').strip()

    if request.method == 'POST':
        form = BookAuthorsForm(request.POST, instance=book)

        queryset = form.fields['allowed_authors'].queryset
        if search_query:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query) |
                models.Q(username__icontains=search_query)
            )
        form.fields['allowed_authors'].queryset = queryset

        if form.is_valid():
            form.save()
            return redirect('manage_book_authors', book_id=book.id)
    else:
        form = BookAuthorsForm(instance=book)

        queryset = form.fields['allowed_authors'].queryset
        if search_query:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query) |
                models.Q(username__icontains=search_query)
            )
        form.fields['allowed_authors'].queryset = queryset

    active_invite = book.author_invites.filter(is_active=True).first()

    return render(
        request,
        'books/manage_book_authors.html',
        {
            'book': book,
            'form': form,
            'search_query': search_query,
            'active_invite': active_invite,
            'unread_count': unread_count,
        }
    )

@login_required
@role_required(['admin'])
def book_article_detail(request, book_id, article_id):
    book = get_object_or_404(Book, id=book_id)

    article = get_object_or_404(
        Article.objects.select_related('author', 'book').prefetch_related(
            'review_assignments__reviewer',
            'review_assignments__reviews',
            'versions'
        ),
        id=article_id,
        book=book
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
                    return redirect('book_article_detail', book_id=book.id, article_id=article.id)
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
                return redirect('book_article_detail', book_id=book.id, article_id=article.id)
    else:
        form = ReviewAssignmentForm(article=article)

    return render(
        request,
        'books/book_article_detail.html',
        {
            'book': book,
            'article': article,
            'form': form,
        }
    )

@login_required
@role_required(['admin'])
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        book.delete()
        return redirect('admin_books')

    return render(
        request,
        'books/delete_book.html',
        {'book': book}
    )


def get_filtered_book_articles(book, request):
    articles = book.articles.select_related('author').prefetch_related('review_assignments', 'versions').all().order_by('-created_at')

    selected_status = request.GET.get('status', '')
    selected_author = request.GET.get('author', '')
    selected_reviewer_filter = request.GET.get('reviewer_filter', '')

    if selected_status:
        articles = articles.filter(status=selected_status)

    if selected_author:
        articles = articles.filter(author_id=selected_author)

    if selected_reviewer_filter == 'with_reviewer':
        articles = articles.filter(review_assignments__isnull=False).distinct()
    elif selected_reviewer_filter == 'without_reviewer':
        articles = articles.filter(review_assignments__isnull=True)

    return articles

@login_required
@role_required(['admin'])
def download_book_articles(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    articles = get_filtered_book_articles(book, request)

    buffer = BytesIO()

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        used_names = {}

        for article in articles:
            latest_version = article.versions.first()

            if latest_version and latest_version.file:
                file_field = latest_version.file
            elif article.file:
                file_field = article.file
            else:
                continue

            original_name = Path(file_field.name).name
            suffix = Path(original_name).suffix or ''
            safe_title = slugify(article.title) or f'article-{article.id}'
            filename = f'{safe_title}{suffix}'

            if filename in used_names:
                used_names[filename] += 1
                filename = f'{safe_title}-{used_names[filename]}{suffix}'
            else:
                used_names[filename] = 1

            file_field.open('rb')
            archive.writestr(filename, file_field.read())
            file_field.close()

    buffer.seek(0)

    zip_name = f'{slugify(book.title) or "book"}-articles.zip'
    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{zip_name}"'
    return response


@login_required
@role_required(['admin'])
def download_article_latest_version(request, book_id, article_id):
    article = get_object_or_404(
        Article.objects.prefetch_related('versions').select_related('book'),
        id=article_id,
        book_id=book_id
    )

    latest_version = article.versions.first()

    if latest_version and latest_version.file:
        file_field = latest_version.file
    elif article.file:
        file_field = article.file
    else:
        raise Http404('No file found for this article.')

    return FileResponse(
        file_field.open('rb'),
        as_attachment=True,
        filename=Path(file_field.name).name
    )


@login_required
@role_required(['admin'])
def create_book_author_invite(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    BookAuthorInvite.objects.filter(
        book=book,
        is_active=True
    ).update(is_active=False)

    BookAuthorInvite.objects.create(
        book=book,
        created_by=request.user
    )

    return redirect('manage_book_authors', book_id=book.id)


def accept_book_author_invite(request, token):
    invite = get_object_or_404(
        BookAuthorInvite.objects.select_related('book'),
        token=token,
        is_active=True
    )

    book = invite.book

    if not request.user.is_authenticated:
        return render(
            request,
            'books/book_author_invite_landing.html',
            {
                'invite': invite,
                'book': book,
            }
        )

    book.allowed_authors.add(request.user)

    messages.success(request, 'You have been added to the allowed authors list for this book.')
    return redirect('choose_book')