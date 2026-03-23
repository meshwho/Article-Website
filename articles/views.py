from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from users.decorators import role_required
from .forms import ArticleCreateForm, ArticleEditForm, ArticleVersionForm
from .models import Article, ArticleVersion
from notifications.models import Notification
from users.models import CustomUser
from django.urls import reverse
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

    return render(
        request,
        'articles/my_articles.html',
        {
            'articles': articles,
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
def create_article(request):
    if request.method == 'POST':
        form = ArticleCreateForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
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
        form = ArticleCreateForm(user=request.user)

    return render(request, 'articles/create_article.html', {'form': form})

@login_required
@role_required(['author'])
def article_detail(request, article_id):
    article = get_object_or_404(
        Article.objects.prefetch_related('review_assignments__reviews'),
        id=article_id,
        author=request.user
    )

    return render(
        request,
        'articles/article_detail.html',
        {'article': article}
    )


@login_required
@role_required(['author'])
def edit_article(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id,
        author=request.user
    )

    if request.method == 'POST':
        form = ArticleEditForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.status = Article.STATUS_UNDER_REVIEW
            article.save()
            return redirect('article_detail', article_id=article.id)
    else:
        form = ArticleEditForm(instance=article)

    return render(
        request,
        'articles/edit_article.html',
        {
            'form': form,
            'article': article,
        }
    )

@login_required
@role_required(['author'])
def upload_new_version(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id,
        author=request.user
    )

    if request.method == 'POST':
        form = ArticleVersionForm(request.POST, request.FILES)
        if form.is_valid():
            last_version = article.versions.first()
            next_version_number = 1 if last_version is None else last_version.version_number + 1

            version = form.save(commit=False)
            version.article = article
            version.version_number = next_version_number
            version.uploaded_by = request.user
            version.save()



            article.file = version.file
            article.status = Article.STATUS_UNDER_REVIEW
            article.save()

            for assignment in article.review_assignments.all():
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
        }
    )