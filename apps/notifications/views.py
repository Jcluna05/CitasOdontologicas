"""
Vistas para la app notifications.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, View

from apps.appointments.models import Appointment

from .models import NotificationLog
from .services import NotificationManager


class NotificationLogListView(LoginRequiredMixin, ListView):
    """Lista de logs de notificaciones."""

    model = NotificationLog
    template_name = 'notifications/notificationlog_list.html'
    context_object_name = 'notifications'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'appointment__patient', 'appointment__professional'
        )

        # Filtros
        status = self.request.GET.get('status')
        channel = self.request.GET.get('channel')
        notification_type = self.request.GET.get('type')

        if status:
            queryset = queryset.filter(status=status)
        if channel:
            queryset = queryset.filter(channel=channel)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        return queryset


class SendReminderView(LoginRequiredMixin, View):
    """Enviar recordatorio manualmente para una cita."""

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        manager = NotificationManager()

        notifications = manager.send_reminder(appointment)

        if notifications and any(n.status == NotificationLog.Status.SENT for n in notifications):
            messages.success(request, 'Recordatorio enviado exitosamente.')
        else:
            messages.error(request, 'Error al enviar el recordatorio.')

        return redirect('appointments:appointment_detail', pk=pk)


class SendNotificationView(LoginRequiredMixin, View):
    """Enviar una notificación específica para una cita."""

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        manager = NotificationManager()

        notification_type = request.POST.get('type', 'reminder')
        channel = request.POST.get('channel', 'whatsapp')

        notification = manager.send_notification(
            appointment=appointment,
            notification_type=notification_type,
            channel=channel,
        )

        if notification and notification.status == NotificationLog.Status.SENT:
            messages.success(request, f'Notificación enviada por {channel}.')
        else:
            messages.error(request, 'Error al enviar la notificación.')

        return redirect('appointments:appointment_detail', pk=pk)
