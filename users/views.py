from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from notifications.models import Notification
from .forms import CustomUserRegistrationForm, ProfileForm


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'users/home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    next_url = request.GET.get('next') or request.POST.get('next')
    hide_role = bool(next_url and '/articles/coauthor-invite/' in next_url)

    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST, hide_role=hide_role)
        if form.is_valid():
            user = form.save(commit=False)

            if hide_role:
                user.role = user.ROLE_AUTHOR

            user.save()
            login(request, user)

            if next_url:
                return redirect(next_url)

            return redirect('dashboard')
    else:
        form = CustomUserRegistrationForm(hide_role=hide_role)

    return render(
        request,
        'users/register.html',
        {
            'form': form,
            'next': next_url,
            'hide_role': hide_role,
        }
    )


@login_required
def dashboard(request):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    if request.user.is_superuser or request.user.role == 'admin':
        return render(request, 'users/admin_dashboard.html', {'unread_count': unread_count})

    if request.user.role == 'author':
        return redirect('my_articles')

    if request.user.role == 'reviewer':
        return redirect('reviewer_assignments')

    return render(request, 'users/dashboard.html', {'unread_count': unread_count})


@login_required
def profile(request):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(
        request,
        'users/profile.html',
        {
            'form': form,
            'unread_count': unread_count,
        }
    )


def custom_logout(request):
    logout(request)
    return redirect('/')