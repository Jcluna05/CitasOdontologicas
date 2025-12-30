"""
Configuración del admin para la app notifications.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """Admin para el modelo NotificationLog."""

    list_display = (
        'appointment', 'notification_type', 'channel',
        'status_badge', 'recipient', 'sent_at'
    )
    list_filter = ('notification_type', 'channel', 'status', 'created_at')
    search_fields = ('appointment__patient__first_name', 'recipient', 'message')
    readonly_fields = ('created_at', 'sent_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Información básica', {
            'fields': ('appointment', 'notification_type', 'channel', 'status')
        }),
        ('Mensaje', {
            'fields': ('recipient', 'message')
        }),
        ('Resultado', {
            'fields': ('response', 'error_message')
        }),
        ('Fechas', {
            'fields': ('scheduled_at', 'sent_at', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'sent': 'info',
            'delivered': 'success',
            'failed': 'danger',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
