from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from notifications.models import Notification
from .forms import CustomUserRegistrationForm


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'users/home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


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


def custom_logout(request):
    logout(request)
    return redirect('/')