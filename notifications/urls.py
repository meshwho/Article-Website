from django.urls import path

from .views import (
    mark_all_notifications_read,
    mark_notification_read,
    my_notifications,
)

urlpatterns = [
    path('my/', my_notifications, name='my_notifications'),
    path('read/<int:notification_id>/', mark_notification_read, name='mark_notification_read'),
    path('read-all/', mark_all_notifications_read, name='mark_all_notifications_read'),
]