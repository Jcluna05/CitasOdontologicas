"""
Servicios de notificación.
"""

import logging
from abc import ABC, abstractmethod
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.clinic.models import MessageTemplate

from .models import NotificationLog

logger = logging.getLogger(__name__)


class NotificationService(ABC):
    """Interfaz base para servicios de notificación."""

    @abstractmethod
    def send(self, recipient: str, message: str) -> tuple[bool, str]:
        """
        Enviar notificación.

        Returns:
            Tuple de (success: bool, response: str)
        """
        pass


class MockWhatsAppService(NotificationService):
    """
    Servicio mock de WhatsApp para desarrollo.
    En producción, implementar con la API real.
    """

    def send(self, recipient: str, message: str) -> tuple[bool, str]:
        logger.info(f"[MOCK WhatsApp] Enviando a {recipient}:\n{message}")
        return True, "Mock: mensaje enviado exitosamente"


class MockSMSService(NotificationService):
    """
    Servicio mock de SMS para desarrollo.
    En producción, implementar con la API real (Twilio, etc.).
    """

    def send(self, recipient: str, message: str) -> tuple[bool, str]:
        logger.info(f"[MOCK SMS] Enviando a {recipient}:\n{message}")
        return True, "Mock: SMS enviado exitosamente"


class EmailService(NotificationService):
    """Servicio de email usando Django mail."""

    def __init__(self, subject: str = "Notificación - Consultorio Odontológico"):
        self.subject = subject

    def send(self, recipient: str, message: str) -> tuple[bool, str]:
        try:
            send_mail(
                subject=self.subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None,
                recipient_list=[recipient],
                fail_silently=False,
            )
            return True, "Email enviado exitosamente"
        except Exception as e:
            logger.error(f"Error enviando email a {recipient}: {str(e)}")
            return False, str(e)


class NotificationManager:
    """
    Manager para el envío de notificaciones.
    """

    def __init__(self):
        self.services = {
            NotificationLog.Channel.WHATSAPP: MockWhatsAppService(),
            NotificationLog.Channel.SMS: MockSMSService(),
            NotificationLog.Channel.EMAIL: EmailService(),
        }

    def get_message_template(self, notification_type: str, clinic) -> str:
        """Obtener plantilla de mensaje."""
        try:
            template = MessageTemplate.objects.get(
                clinic=clinic,
                template_type=notification_type,
                is_active=True,
            )
            return template.message
        except MessageTemplate.DoesNotExist:
            # Plantillas por defecto
            defaults = {
                'reminder': (
                    "Recordatorio de cita:\n"
                    "Paciente: {paciente}\n"
                    "Fecha: {fecha}\n"
                    "Hora: {hora}\n"
                    "Procedimiento: {procedimiento}\n"
                    "Dr(a): {doctor}"
                ),
                'confirmation': (
                    "Su cita ha sido confirmada:\n"
                    "Fecha: {fecha}\n"
                    "Hora: {hora}\n"
                    "Dr(a): {doctor}"
                ),
                'cancellation': (
                    "Su cita ha sido cancelada:\n"
                    "Fecha original: {fecha}\n"
                    "Hora: {hora}\n"
                    "Por favor contacte al consultorio para reprogramar."
                ),
                'reschedule': (
                    "Su cita ha sido reprogramada:\n"
                    "Nueva fecha: {fecha}\n"
                    "Nueva hora: {hora}\n"
                    "Dr(a): {doctor}"
                ),
            }
            return defaults.get(notification_type, "")

    def build_context(self, appointment: Appointment) -> dict:
        """Construir contexto para las plantillas."""
        return {
            'paciente': appointment.patient.full_name,
            'fecha': appointment.date.strftime('%d/%m/%Y'),
            'hora': appointment.start_time.strftime('%H:%M'),
            'procedimiento': appointment.procedure_type.name if appointment.procedure_type else 'Consulta',
            'doctor': str(appointment.professional),
            'consultorio': appointment.clinic.name if appointment.clinic else '',
            'telefono': appointment.clinic.phone if appointment.clinic else '',
        }

    def render_message(self, template: str, context: dict) -> str:
        """Renderizar mensaje con el contexto."""
        message = template
        for key, value in context.items():
            message = message.replace(f'{{{key}}}', str(value))
        return message

    def send_notification(
        self,
        appointment: Appointment,
        notification_type: str,
        channel: str,
        recipient: str = None,
    ) -> NotificationLog:
        """
        Enviar una notificación para una cita.

        Args:
            appointment: La cita
            notification_type: Tipo de notificación (reminder, confirmation, etc.)
            channel: Canal de envío (whatsapp, sms, email)
            recipient: Destinatario (opcional, se usa el del paciente)

        Returns:
            NotificationLog creado
        """
        # Determinar destinatario
        if not recipient:
            if channel == NotificationLog.Channel.EMAIL:
                recipient = appointment.patient.email
            else:
                recipient = appointment.patient.whatsapp or appointment.patient.phone

        if not recipient:
            logger.warning(f"No hay destinatario para {channel} en cita {appointment.id}")
            return None

        # Construir mensaje
        template = self.get_message_template(notification_type, appointment.clinic)
        context = self.build_context(appointment)
        message = self.render_message(template, context)

        # Crear log
        notification = NotificationLog.objects.create(
            appointment=appointment,
            notification_type=notification_type,
            channel=channel,
            recipient=recipient,
            message=message,
            status=NotificationLog.Status.PENDING,
        )

        # Enviar
        service = self.services.get(channel)
        if service:
            success, response = service.send(recipient, message)
            if success:
                notification.mark_as_sent(response)
                # Actualizar bandera en la cita si es recordatorio
                if notification_type == NotificationLog.NotificationType.REMINDER:
                    appointment.reminder_sent = True
                    appointment.reminder_sent_at = timezone.now()
                    appointment.save(update_fields=['reminder_sent', 'reminder_sent_at'])
            else:
                notification.mark_as_failed(response)
        else:
            notification.mark_as_failed(f"Servicio no disponible para {channel}")

        return notification

    def send_reminder(self, appointment: Appointment) -> list[NotificationLog]:
        """
        Enviar recordatorio por todos los canales disponibles.
        """
        notifications = []

        # WhatsApp (preferido)
        if appointment.patient.whatsapp or appointment.patient.phone:
            notification = self.send_notification(
                appointment,
                NotificationLog.NotificationType.REMINDER,
                NotificationLog.Channel.WHATSAPP,
            )
            if notification:
                notifications.append(notification)

        # Email (si tiene)
        if appointment.patient.email:
            notification = self.send_notification(
                appointment,
                NotificationLog.NotificationType.REMINDER,
                NotificationLog.Channel.EMAIL,
            )
            if notification:
                notifications.append(notification)

        return notifications


def get_appointments_for_reminder(hours_before: int = 24):
    """
    Obtener citas que necesitan recordatorio.

    Args:
        hours_before: Horas antes de la cita para enviar recordatorio

    Returns:
        QuerySet de citas
    """
    now = timezone.now()
    reminder_time = now + timedelta(hours=hours_before)

    # Citas entre ahora y el tiempo de recordatorio
    appointments = Appointment.objects.filter(
        date=reminder_time.date(),
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
        reminder_sent=False,
    ).select_related('patient', 'professional', 'procedure_type', 'clinic')

    return appointments


def send_daily_reminders():
    """
    Función para enviar recordatorios diarios.
    Se puede llamar desde un cron job o management command.
    """
    manager = NotificationManager()
    appointments = get_appointments_for_reminder(24)

    sent_count = 0
    failed_count = 0

    for appointment in appointments:
        try:
            notifications = manager.send_reminder(appointment)
            if notifications and any(n.status == NotificationLog.Status.SENT for n in notifications):
                sent_count += 1
            else:
                failed_count += 1
        except Exception as e:
            logger.error(f"Error enviando recordatorio para cita {appointment.id}: {str(e)}")
            failed_count += 1

    logger.info(f"Recordatorios enviados: {sent_count}, fallidos: {failed_count}")
    return sent_count, failed_count
