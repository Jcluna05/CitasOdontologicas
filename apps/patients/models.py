"""
Modelos para la gestión de pacientes.
"""

from datetime import date

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from apps.clinic.models import Clinic


class Patient(models.Model):
    """
    Modelo para pacientes del consultorio.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Activo')
        INACTIVE = 'inactive', _('Inactivo')
        BLOCKED = 'blocked', _('Bloqueado')

    # Información básica
    medical_record_number = models.CharField(
        _('N° historia clínica'),
        max_length=20,
        unique=True,
    )
    first_name = models.CharField(_('nombres'), max_length=100)
    last_name = models.CharField(_('apellidos'), max_length=100)
    birth_date = models.DateField(_('fecha de nacimiento'), null=True, blank=True)
    gender = models.CharField(
        _('género'),
        max_length=1,
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        blank=True,
    )

    # Contacto
    phone = models.CharField(_('teléfono'), max_length=20)
    whatsapp = models.CharField(_('WhatsApp'), max_length=20, blank=True)
    email = models.EmailField(_('correo electrónico'), blank=True)
    address = models.TextField(_('dirección'), blank=True)

    # Triage y observaciones médicas
    has_anxiety = models.BooleanField(_('ansiedad dental'), default=False)
    has_allergies = models.BooleanField(_('tiene alergias'), default=False)
    allergies_detail = models.TextField(_('detalle alergias'), blank=True)
    has_acute_pain = models.BooleanField(_('dolor agudo'), default=False)
    is_child = models.BooleanField(_('es niño'), default=False)
    is_elderly = models.BooleanField(_('es adulto mayor'), default=False)
    medical_notes = models.TextField(_('notas médicas'), blank=True)
    observations = models.TextField(_('observaciones generales'), blank=True)

    # Control de inasistencias
    no_show_count = models.PositiveIntegerField(
        _('inasistencias'),
        default=0,
        validators=[MinValueValidator(0)],
    )
    requires_advance_payment = models.BooleanField(
        _('requiere anticipo'),
        default=False,
        help_text=_('Activado automáticamente después de 2 inasistencias')
    )

    # Estado
    status = models.CharField(
        _('estado'),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    # Relaciones
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='patients',
        verbose_name=_('consultorio'),
        null=True,
        blank=True,
    )

    # Timestamps
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)

    class Meta:
        verbose_name = _('paciente')
        verbose_name_plural = _('pacientes')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'

    @property
    def full_name(self):
        """Nombre completo del paciente."""
        return f'{self.first_name} {self.last_name}'

    @property
    def age(self):
        """Calcula la edad del paciente."""
        if not self.birth_date:
            return None
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    @property
    def age_display(self):
        """Muestra la edad formateada."""
        age = self.age
        if age is None:
            return 'No especificada'
        return f'{age} años'

    @property
    def has_warnings(self):
        """Indica si el paciente tiene alertas."""
        return (
            self.has_anxiety or
            self.has_allergies or
            self.has_acute_pain or
            self.no_show_count >= 1
        )

    @property
    def triage_alerts(self):
        """Lista de alertas de triage."""
        alerts = []
        if self.has_acute_pain:
            alerts.append({'type': 'danger', 'message': 'Dolor agudo'})
        if self.has_allergies:
            alerts.append({
                'type': 'warning',
                'message': f'Alergias: {self.allergies_detail or "Ver historial"}'
            })
        if self.has_anxiety:
            alerts.append({'type': 'info', 'message': 'Ansiedad dental'})
        if self.is_child:
            alerts.append({'type': 'info', 'message': 'Paciente pediátrico'})
        if self.is_elderly:
            alerts.append({'type': 'info', 'message': 'Adulto mayor'})
        if self.no_show_count >= 2:
            alerts.append({
                'type': 'warning',
                'message': f'Inasistencias: {self.no_show_count}'
            })
        elif self.no_show_count == 1:
            alerts.append({
                'type': 'secondary',
                'message': 'Advertencia: 1 inasistencia'
            })
        return alerts

    def register_no_show(self):
        """Registrar una inasistencia."""
        self.no_show_count += 1
        if self.no_show_count >= 2:
            self.requires_advance_payment = True
        self.save(update_fields=['no_show_count', 'requires_advance_payment'])

    def reset_no_shows(self):
        """Reiniciar el contador de inasistencias."""
        self.no_show_count = 0
        self.requires_advance_payment = False
        self.save(update_fields=['no_show_count', 'requires_advance_payment'])

    @classmethod
    def generate_medical_record_number(cls):
        """Generar un número de historia clínica único."""
        from django.utils import timezone
        import random
        year = timezone.now().year
        while True:
            number = f'HC-{year}-{random.randint(1000, 9999)}'
            if not cls.objects.filter(medical_record_number=number).exists():
                return number


class PatientEvent(models.Model):
    """
    Modelo para registrar eventos/notas del paciente.
    """

    class EventType(models.TextChoices):
        NOTE = 'note', _('Nota')
        NO_SHOW = 'no_show', _('Inasistencia')
        ALERT = 'alert', _('Alerta')
        MEDICAL = 'medical', _('Médico')

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name=_('paciente'),
    )
    event_type = models.CharField(
        _('tipo'),
        max_length=20,
        choices=EventType.choices,
    )
    description = models.TextField(_('descripción'))
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('creado por'),
    )
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)

    class Meta:
        verbose_name = _('evento de paciente')
        verbose_name_plural = _('eventos de pacientes')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.patient} - {self.get_event_type_display()} - {self.created_at}'
