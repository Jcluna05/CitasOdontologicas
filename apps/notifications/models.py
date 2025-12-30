"""
Modelos para el sistema de notificaciones.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.appointments.models import Appointment


class NotificationLog(models.Model):
    """
    Registro de notificaciones enviadas.
    """

    class Channel(models.TextChoices):
        WHATSAPP = 'whatsapp', _('WhatsApp')
        SMS = 'sms', _('SMS')
        EMAIL = 'email', _('Email')
        PHONE = 'phone', _('Llamada')

    class NotificationType(models.TextChoices):
        REMINDER = 'reminder', _('Recordatorio')
        CONFIRMATION = 'confirmation', _('Confirmación')
        CANCELLATION = 'cancellation', _('Cancelación')
        RESCHEDULE = 'reschedule', _('Reprogramación')

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pendiente')
        SENT = 'sent', _('Enviado')
        DELIVERED = 'delivered', _('Entregado')
        FAILED = 'failed', _('Fallido')

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('cita'),
    )
    notification_type = models.CharField(
        _('tipo'),
        max_length=20,
        choices=NotificationType.choices,
    )
    channel = models.CharField(
        _('canal'),
        max_length=20,
        choices=Channel.choices,
    )
    status = models.CharField(
        _('estado'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    recipient = models.CharField(
        _('destinatario'),
        max_length=200,
        help_text=_('Teléfono o email del destinatario')
    )
    message = models.TextField(_('mensaje'))
    response = models.TextField(
        _('respuesta'),
        blank=True,
        help_text=_('Respuesta del servicio de envío')
    )
    error_message = models.TextField(_('error'), blank=True)

    scheduled_at = models.DateTimeField(_('programado para'), null=True, blank=True)
    sent_at = models.DateTimeField(_('enviado el'), null=True, blank=True)
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)

    class Meta:
        verbose_name = _('log de notificación')
        verbose_name_plural = _('logs de notificaciones')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_notification_type_display()} - {self.appointment} - {self.get_status_display()}'

    def mark_as_sent(self, response=''):
        """Marcar la notificación como enviada."""
        from django.utils import timezone
        self.status = self.Status.SENT
        self.sent_at = timezone.now()
        self.response = response
        self.save()

    def mark_as_failed(self, error=''):
        """Marcar la notificación como fallida."""
        self.status = self.Status.FAILED
        self.error_message = error
        self.save()
