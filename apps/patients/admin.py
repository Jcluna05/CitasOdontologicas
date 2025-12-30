"""
Configuración del admin para la app patients.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Patient, PatientEvent


class PatientEventInline(admin.TabularInline):
    """Inline para eventos del paciente."""

    model = PatientEvent
    extra = 0
    readonly_fields = ('created_at', 'created_by')
    fields = ('event_type', 'description', 'created_by', 'created_at')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Admin para el modelo Patient."""

    list_display = (
        'medical_record_number', 'full_name', 'phone',
        'age_display', 'status_badge', 'no_show_count'
    )
    list_filter = ('status', 'has_anxiety', 'has_allergies', 'is_child', 'is_elderly')
    search_fields = ('first_name', 'last_name', 'medical_record_number', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at', 'age_display')
    inlines = [PatientEventInline]

    fieldsets = (
        ('Información básica', {
            'fields': (
                'medical_record_number', 'first_name', 'last_name',
                'birth_date', 'age_display', 'gender'
            )
        }),
        ('Contacto', {
            'fields': ('phone', 'whatsapp', 'email', 'address')
        }),
        ('Información médica', {
            'fields': (
                'has_anxiety', 'has_allergies', 'allergies_detail',
                'has_acute_pain', 'is_child', 'is_elderly',
                'medical_notes', 'observations'
            )
        }),
        ('Control de inasistencias', {
            'fields': ('no_show_count', 'requires_advance_payment')
        }),
        ('Estado', {
            'fields': ('status', 'clinic')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'active': 'success',
            'inactive': 'secondary',
            'blocked': 'danger',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'


@admin.register(PatientEvent)
class PatientEventAdmin(admin.ModelAdmin):
    """Admin para el modelo PatientEvent."""

    list_display = ('patient', 'event_type', 'description', 'created_by', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'description')
    readonly_fields = ('created_at',)
