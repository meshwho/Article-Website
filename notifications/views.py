from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


@login_required
def my_notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(
        request,
        'notifications/my_notifications.html',
        {'notifications': notifications}
    )


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.is_read = True
    notification.save()

    if notification.link:
        return redirect(notification.link)

    return redirect('my_notifications')