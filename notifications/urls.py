from django.urls import path

from .views import mark_notification_read, my_notifications

urlpatterns = [
    path('my/', my_notifications, name='my_notifications'),
    path('read/<int:notification_id>/', mark_notification_read, name='mark_notification_read'),
]