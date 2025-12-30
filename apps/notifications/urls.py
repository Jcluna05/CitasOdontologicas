"""
URLs para la app notifications.
"""

from django.urls import path

from .views import (
    NotificationLogListView,
    SendReminderView,
    SendNotificationView,
)

app_name = 'notifications'

urlpatterns = [
    path('logs/', NotificationLogListView.as_view(), name='log_list'),
    path('send-reminder/<int:pk>/', SendReminderView.as_view(), name='send_reminder'),
    path('send/<int:pk>/', SendNotificationView.as_view(), name='send_notification'),
]
