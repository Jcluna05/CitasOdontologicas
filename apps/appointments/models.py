"""
Modelos para la gestión de citas odontológicas.
"""

from datetime import timedelta

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.clinic.models import Clinic, Professional
from apps.patients.models import Patient


class ProcedureType(models.Model):
    """
    Catálogo de tipos de procedimientos/citas.
    """

    name = models.CharField(_('nombre'), max_length=100)
    description = models.TextField(_('descripción'), blank=True)
    duration_minutes = models.PositiveIntegerField(
        _('duración (minutos)'),
        default=30,
    )
    color = models.CharField(
        _('color'),
        max_length=7,
        default='#1D4ED8',
        help_text=_('Color en formato hexadecimal')
    )
    requires_confirmation = models.BooleanField(
        _('requiere confirmación'),
        default=True,
    )
    is_active = models.BooleanField(_('activo'), default=True)
    order = models.PositiveIntegerField(_('orden'), default=0)

    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)

    class Meta:
        verbose_name = _('tipo de procedimiento')
        verbose_name_plural = _('tipos de procedimientos')
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.name} ({self.duration_minutes} min)'


class Appointment(models.Model):
    """
    Modelo principal de citas.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pendiente')
        CONFIRMED = 'confirmed', _('Confirmada')
        ATTENDED = 'attended', _('Atendido')
        CANCELLED = 'cancelled', _('Cancelado')
        NO_SHOW = 'no_show', _('No asistió')

    # Relaciones principales
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('paciente'),
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('profesional'),
    )
    procedure_type = models.ForeignKey(
        ProcedureType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='appointments',
        verbose_name=_('procedimiento'),
    )
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('consultorio'),
        null=True,
    )

    # Fecha y hora
    date = models.DateField(_('fecha'))
    start_time = models.TimeField(_('hora inicio'))
    end_time = models.TimeField(_('hora fin'))

    # Estado
    status = models.CharField(
        _('estado'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # Información adicional
    notes = models.TextField(_('notas'), blank=True)
    cancellation_reason = models.TextField(_('motivo de cancelación'), blank=True)
    cancelled_at = models.DateTimeField(_('cancelado el'), null=True, blank=True)

    # Control de recordatorios
    reminder_sent = models.BooleanField(_('recordatorio enviado'), default=False)
    reminder_sent_at = models.DateTimeField(_('recordatorio enviado el'), null=True, blank=True)
    confirmed_at = models.DateTimeField(_('confirmado el'), null=True, blank=True)

    # Timestamps y auditoría
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_appointments',
        verbose_name=_('creado por'),
    )
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)

    class Meta:
        verbose_name = _('cita')
        verbose_name_plural = _('citas')
        ordering = ['-date', '-start_time']
        indexes = [
            models.Index(fields=['date', 'professional']),
            models.Index(fields=['date', 'status']),
            models.Index(fields=['patient', 'date']),
        ]

    def __str__(self):
        return f'{self.patient} - {self.date} {self.start_time}'

    def clean(self):
        """Validaciones del modelo."""
        errors = {}

        # Validar que end_time sea posterior a start_time
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                errors['end_time'] = _(
                    'La hora de fin debe ser posterior a la hora de inicio.'
                )

        # Validar solapamiento de citas por profesional
        if self.date and self.start_time and self.end_time and self.professional:
            overlapping = Appointment.objects.filter(
                professional=self.professional,
                date=self.date,
                status__in=[self.Status.PENDING, self.Status.CONFIRMED],
            ).exclude(pk=self.pk)

            for apt in overlapping:
                if (self.start_time < apt.end_time and self.end_time > apt.start_time):
                    errors['start_time'] = _(
                        f'El profesional ya tiene una cita de {apt.start_time} a {apt.end_time}.'
                    )
                    break

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Auto-calcular end_time si no está definido
        if self.start_time and self.procedure_type and not self.end_time:
            from datetime import datetime, date as date_type
            start_datetime = datetime.combine(date_type.today(), self.start_time)
            end_datetime = start_datetime + timedelta(minutes=self.procedure_type.duration_minutes)
            self.end_time = end_datetime.time()

        # Actualizar timestamps de estados
        if self.status == self.Status.CANCELLED and not self.cancelled_at:
            self.cancelled_at = timezone.now()
        if self.status == self.Status.CONFIRMED and not self.confirmed_at:
            self.confirmed_at = timezone.now()

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def duration_minutes(self):
        """Duración de la cita en minutos."""
        from datetime import datetime, date
        start = datetime.combine(date.today(), self.start_time)
        end = datetime.combine(date.today(), self.end_time)
        return int((end - start).total_seconds() / 60)

    @property
    def is_today(self):
        """Indica si la cita es hoy."""
        return self.date == timezone.now().date()

    @property
    def is_past(self):
        """Indica si la cita ya pasó."""
        now = timezone.now()
        from datetime import datetime
        apt_datetime = datetime.combine(self.date, self.end_time)
        apt_datetime = timezone.make_aware(apt_datetime)
        return apt_datetime < now

    @property
    def can_be_cancelled(self):
        """Indica si la cita puede ser cancelada."""
        return self.status in [self.Status.PENDING, self.Status.CONFIRMED]

    @property
    def can_be_confirmed(self):
        """Indica si la cita puede ser confirmada."""
        return self.status == self.Status.PENDING

    @property
    def status_color(self):
        """Color del estado para la UI."""
        colors = {
            self.Status.PENDING: 'warning',
            self.Status.CONFIRMED: 'info',
            self.Status.ATTENDED: 'success',
            self.Status.CANCELLED: 'danger',
            self.Status.NO_SHOW: 'dark',
        }
        return colors.get(self.status, 'secondary')

    def get_whatsapp_message(self):
        """Genera el mensaje formateado para WhatsApp."""
        clinic = self.clinic or Clinic.get_default()
        procedure_name = self.procedure_type.name if self.procedure_type else 'Consulta'

        message = f"""*CITA ODONTOLÓGICA*

*Paciente:* {self.patient.full_name}
*Fecha:* {self.date.strftime('%d/%m/%Y')}
*Hora:* {self.start_time.strftime('%H:%M')}
*Procedimiento:* {procedure_name}
*Doctor/a:* {self.professional}

*Consultorio:* {clinic.name}
*Dirección:* {clinic.address}
*Teléfono:* {clinic.phone}"""

        if self.notes:
            message += f"\n\n*Observaciones:* {self.notes}"

        return message

    def confirm(self):
        """Confirmar la cita."""
        if self.can_be_confirmed:
            self.status = self.Status.CONFIRMED
            self.confirmed_at = timezone.now()
            self.save()
            return True
        return False

    def cancel(self, reason=''):
        """Cancelar la cita."""
        if self.can_be_cancelled:
            self.status = self.Status.CANCELLED
            self.cancellation_reason = reason
            self.cancelled_at = timezone.now()
            self.save()
            return True
        return False

    def mark_attended(self):
        """Marcar la cita como atendida."""
        if self.status in [self.Status.PENDING, self.Status.CONFIRMED]:
            self.status = self.Status.ATTENDED
            self.save()
            return True
        return False

    def mark_no_show(self):
        """Marcar la cita como no asistió."""
        if self.status in [self.Status.PENDING, self.Status.CONFIRMED]:
            self.status = self.Status.NO_SHOW
            self.patient.register_no_show()
            self.save()
            return True
        return False


class AppointmentStatusLog(models.Model):
    """
    Registro de auditoría para cambios de estado en citas.
    """

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='status_logs',
        verbose_name=_('cita'),
    )
    previous_status = models.CharField(
        _('estado anterior'),
        max_length=20,
        choices=Appointment.Status.choices,
        blank=True,
    )
    new_status = models.CharField(
        _('nuevo estado'),
        max_length=20,
        choices=Appointment.Status.choices,
    )
    changed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('cambiado por'),
    )
    notes = models.TextField(_('notas'), blank=True)
    created_at = models.DateTimeField(_('fecha'), auto_now_add=True)

    class Meta:
        verbose_name = _('log de estado de cita')
        verbose_name_plural = _('logs de estados de citas')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.appointment} - {self.previous_status} → {self.new_status}'
