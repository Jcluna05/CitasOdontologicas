"""
Configuración del admin para la app appointments.
"""

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import ProcedureType, Appointment, AppointmentStatusLog


@admin.register(ProcedureType)
class ProcedureTypeAdmin(ModelAdmin):
    """Admin para el modelo ProcedureType."""

    list_display = (
        'name', 'duration_minutes', 'color_display',
        'requires_confirmation', 'is_active', 'order'
    )
    list_filter = ('is_active', 'requires_confirmation')
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_active')
    ordering = ('order', 'name')

    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 15px; '
            'border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'


class AppointmentStatusLogInline(TabularInline):
    """Inline para logs de estado."""

    model = AppointmentStatusLog
    extra = 0
    readonly_fields = ('previous_status', 'new_status', 'changed_by', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
    """Admin para el modelo Appointment."""

    list_display = (
        'patient', 'professional', 'date', 'start_time', 'end_time',
        'procedure_type', 'status_badge', 'reminder_sent'
    )
    list_filter = ('status', 'date', 'professional', 'procedure_type')
    search_fields = (
        'patient__first_name', 'patient__last_name',
        'patient__medical_record_number', 'notes'
    )
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at', 'cancelled_at', 'confirmed_at')
    inlines = [AppointmentStatusLogInline]

    fieldsets = (
        ('Información principal', {
            'fields': ('patient', 'professional', 'procedure_type', 'clinic')
        }),
        ('Fecha y hora', {
            'fields': ('date', 'start_time', 'end_time')
        }),
        ('Estado', {
            'fields': ('status', 'notes')
        }),
        ('Cancelación', {
            'fields': ('cancellation_reason', 'cancelled_at'),
            'classes': ('collapse',)
        }),
        ('Recordatorios', {
            'fields': ('reminder_sent', 'reminder_sent_at', 'confirmed_at'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'attended': 'success',
            'cancelled': 'danger',
            'no_show': 'dark',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'


@admin.register(AppointmentStatusLog)
class AppointmentStatusLogAdmin(ModelAdmin):
    """Admin para el modelo AppointmentStatusLog."""

    list_display = (
        'appointment', 'previous_status', 'new_status',
        'changed_by', 'created_at'
    )
    list_filter = ('new_status', 'created_at')
    readonly_fields = ('appointment', 'previous_status', 'new_status', 'changed_by', 'created_at')
    date_hierarchy = 'created_at'
