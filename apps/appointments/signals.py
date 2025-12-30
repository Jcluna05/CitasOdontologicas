"""
Signals para la app appointments.
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Appointment, AppointmentStatusLog


@receiver(pre_save, sender=Appointment)
def track_status_change(sender, instance, **kwargs):
    """Rastrear cambios de estado antes de guardar."""
    if instance.pk:
        try:
            old_instance = Appointment.objects.get(pk=instance.pk)
            instance._previous_status = old_instance.status
        except Appointment.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Appointment)
def log_status_change(sender, instance, created, **kwargs):
    """Registrar cambios de estado después de guardar."""
    previous_status = getattr(instance, '_previous_status', None)

    # Si es nueva cita o el estado cambió
    if created or (previous_status and previous_status != instance.status):
        AppointmentStatusLog.objects.create(
            appointment=instance,
            previous_status=previous_status or '',
            new_status=instance.status,
            changed_by=getattr(instance, '_changed_by', None),
        )
