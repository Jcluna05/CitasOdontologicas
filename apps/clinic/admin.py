"""
Configuración del admin para la app clinic.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Clinic, Professional, Schedule, MessageTemplate


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    """Admin para el modelo Clinic."""

    list_display = ('name', 'phone', 'email', 'updated_at')
    search_fields = ('name', 'email')

    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'logo')
        }),
        ('Contacto', {
            'fields': ('phone', 'whatsapp', 'email', 'address')
        }),
        ('Configuración', {
            'fields': ('appointment_duration_default', 'allow_online_booking')
        }),
    )


class ScheduleInline(admin.TabularInline):
    """Inline para horarios."""

    model = Schedule
    extra = 0
    fields = ('weekday', 'start_time', 'end_time', 'is_active')


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    """Admin para el modelo Professional."""

    list_display = ('__str__', 'specialty', 'color_display', 'is_active')
    list_filter = ('is_active', 'clinic', 'specialty')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    inlines = [ScheduleInline]

    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'clinic')
        }),
        ('Información profesional', {
            'fields': ('specialty', 'license_number')
        }),
        ('Visualización', {
            'fields': ('color', 'is_active')
        }),
    )

    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 15px; '
            'border-radius: 3px;">&nbsp;</span>',
            obj.color
        )
    color_display.short_description = 'Color'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """Admin para el modelo Schedule."""

    list_display = ('__str__', 'weekday', 'start_time', 'end_time', 'is_active')
    list_filter = ('weekday', 'is_active', 'professional', 'clinic')
    ordering = ('weekday', 'start_time')


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    """Admin para el modelo MessageTemplate."""

    list_display = ('template_type', 'clinic', 'subject', 'is_active')
    list_filter = ('template_type', 'is_active', 'clinic')
    search_fields = ('subject', 'message')
