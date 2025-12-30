"""
Modelos para la gestión del consultorio odontológico.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.accounts.models import User


class Clinic(models.Model):
    """
    Modelo para la configuración del consultorio.
    Diseñado como singleton para un solo consultorio,
    pero preparado para multi-consultorio si es necesario.
    """

    name = models.CharField(_('nombre'), max_length=200)
    phone = models.CharField(_('teléfono'), max_length=20)
    whatsapp = models.CharField(_('WhatsApp'), max_length=20, blank=True)
    email = models.EmailField(_('correo electrónico'))
    address = models.TextField(_('dirección'))
    logo = models.ImageField(
        _('logo'),
        upload_to='clinic/',
        blank=True,
        null=True,
    )

    # Configuración adicional
    appointment_duration_default = models.PositiveIntegerField(
        _('duración por defecto (min)'),
        default=30,
        help_text=_('Duración por defecto de una cita en minutos')
    )
    allow_online_booking = models.BooleanField(
        _('permitir reservas online'),
        default=False,
    )

    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)

    class Meta:
        verbose_name = _('consultorio')
        verbose_name_plural = _('consultorios')

    def __str__(self):
        return self.name

    @classmethod
    def get_default(cls):
        """Obtener el consultorio por defecto (singleton)."""
        clinic, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'name': 'Consultorio Odontológico',
                'phone': '000-000-0000',
                'email': 'contacto@clinica.com',
                'address': 'Dirección del consultorio',
            }
        )
        return clinic


class Professional(models.Model):
    """
    Modelo para los profesionales (odontólogos).
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='professional_profile',
        verbose_name=_('usuario'),
    )
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='professionals',
        verbose_name=_('consultorio'),
    )
    specialty = models.CharField(
        _('especialidad'),
        max_length=100,
        blank=True,
        help_text=_('Ej: Odontología General, Ortodoncia, Endodoncia')
    )
    license_number = models.CharField(
        _('número de colegiatura'),
        max_length=50,
        blank=True,
    )
    color = models.CharField(
        _('color'),
        max_length=7,
        default='#1D4ED8',
        help_text=_('Color para identificar en la agenda (formato hex)')
    )
    is_active = models.BooleanField(_('activo'), default=True)

    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)

    class Meta:
        verbose_name = _('profesional')
        verbose_name_plural = _('profesionales')
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f'Dr(a). {self.user.get_full_name()}'

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email


class Schedule(models.Model):
    """
    Modelo para los horarios de atención por día de semana.
    """

    class Weekday(models.IntegerChoices):
        MONDAY = 0, _('Lunes')
        TUESDAY = 1, _('Martes')
        WEDNESDAY = 2, _('Miércoles')
        THURSDAY = 3, _('Jueves')
        FRIDAY = 4, _('Viernes')
        SATURDAY = 5, _('Sábado')
        SUNDAY = 6, _('Domingo')

    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name=_('consultorio'),
        null=True,
        blank=True,
    )
    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name=_('profesional'),
        null=True,
        blank=True,
        help_text=_('Dejar vacío para horario general del consultorio')
    )
    weekday = models.IntegerField(
        _('día de la semana'),
        choices=Weekday.choices,
    )
    start_time = models.TimeField(_('hora inicio'))
    end_time = models.TimeField(_('hora fin'))
    is_active = models.BooleanField(_('activo'), default=True)

    class Meta:
        verbose_name = _('horario')
        verbose_name_plural = _('horarios')
        ordering = ['weekday', 'start_time']
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_time__lt=models.F('end_time')),
                name='schedule_start_before_end',
            ),
        ]

    def __str__(self):
        owner = self.professional or self.clinic or 'General'
        return f'{owner} - {self.get_weekday_display()}: {self.start_time} - {self.end_time}'

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time >= self.end_time:
            raise ValidationError({
                'end_time': _('La hora de fin debe ser posterior a la hora de inicio.')
            })


class MessageTemplate(models.Model):
    """
    Plantillas de mensajes para notificaciones.
    """

    class TemplateType(models.TextChoices):
        CONFIRMATION = 'confirmation', _('Confirmación')
        REMINDER = 'reminder', _('Recordatorio')
        CANCELLATION = 'cancellation', _('Cancelación')
        RESCHEDULE = 'reschedule', _('Reprogramación')

    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='message_templates',
        verbose_name=_('consultorio'),
    )
    template_type = models.CharField(
        _('tipo'),
        max_length=20,
        choices=TemplateType.choices,
    )
    subject = models.CharField(
        _('asunto'),
        max_length=200,
        blank=True,
        help_text=_('Para emails')
    )
    message = models.TextField(
        _('mensaje'),
        help_text=_(
            'Variables disponibles: {paciente}, {fecha}, {hora}, '
            '{procedimiento}, {doctor}, {consultorio}, {telefono}'
        )
    )
    is_active = models.BooleanField(_('activo'), default=True)

    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)

    class Meta:
        verbose_name = _('plantilla de mensaje')
        verbose_name_plural = _('plantillas de mensajes')
        unique_together = ['clinic', 'template_type']

    def __str__(self):
        return f'{self.get_template_type_display()} - {self.clinic}'

    def render(self, context: dict) -> str:
        """Renderizar el mensaje con el contexto dado."""
        message = self.message
        for key, value in context.items():
            message = message.replace(f'{{{key}}}', str(value))
        return message
