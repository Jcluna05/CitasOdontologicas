"""
Signals para la app accounts.
"""

from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


@receiver(post_save, sender=User)
def assign_user_to_group(sender, instance, created, **kwargs):
    """Asignar usuario al grupo correspondiente según su rol."""
    if created:
        group_mapping = {
            User.Role.ADMIN: 'Administradores',
            User.Role.RECEPTION: 'Recepción',
            User.Role.PROFESSIONAL: 'Profesionales',
        }

        group_name = group_mapping.get(instance.role)
        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            instance.groups.add(group)
