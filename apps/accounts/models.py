"""
Modelos de usuarios y autenticación para el sistema de citas odontológicas.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager personalizado para el modelo User."""

    def create_user(self, email, password=None, **extra_fields):
        """Crear y guardar un usuario regular."""
        if not email:
            raise ValueError(_('El email es obligatorio'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Crear y guardar un superusuario."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser debe tener is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser debe tener is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Modelo de usuario personalizado.
    Usa email como identificador único en lugar de username.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', _('Administrador')
        RECEPTION = 'reception', _('Recepción')
        PROFESSIONAL = 'professional', _('Profesional')

    # Quitar username, usar email
    username = None
    email = models.EmailField(_('correo electrónico'), unique=True)

    # Campos adicionales
    role = models.CharField(
        _('rol'),
        max_length=20,
        choices=Role.choices,
        default=Role.RECEPTION,
    )
    phone = models.CharField(_('teléfono'), max_length=20, blank=True)
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        blank=True,
        null=True,
    )

    # Configuración
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        """Retorna el nombre completo."""
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        """Retorna el nombre corto."""
        return self.first_name

    @property
    def is_admin(self):
        """Verifica si es administrador."""
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_reception(self):
        """Verifica si es recepción."""
        return self.role == self.Role.RECEPTION

    @property
    def is_professional(self):
        """Verifica si es profesional."""
        return self.role == self.Role.PROFESSIONAL
