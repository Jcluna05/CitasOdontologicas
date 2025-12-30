"""
Serializers para la API de clinic.
"""

from rest_framework import serializers

from .models import Clinic, Professional, Schedule, MessageTemplate


class ClinicSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Clinic."""

    class Meta:
        model = Clinic
        fields = [
            'id', 'name', 'phone', 'whatsapp', 'email', 'address',
            'appointment_duration_default', 'allow_online_booking',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Schedule."""

    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)

    class Meta:
        model = Schedule
        fields = [
            'id', 'clinic', 'professional', 'weekday', 'weekday_display',
            'start_time', 'end_time', 'is_active'
        ]
        read_only_fields = ['id']


class ProfessionalSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Professional."""

    full_name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    schedules = ScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Professional
        fields = [
            'id', 'user', 'clinic', 'full_name', 'email',
            'specialty', 'license_number', 'color', 'is_active',
            'schedules', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProfessionalListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Professional
        fields = ['id', 'full_name', 'specialty', 'color', 'is_active']


class MessageTemplateSerializer(serializers.ModelSerializer):
    """Serializer para el modelo MessageTemplate."""

    template_type_display = serializers.CharField(
        source='get_template_type_display',
        read_only=True
    )

    class Meta:
        model = MessageTemplate
        fields = [
            'id', 'clinic', 'template_type', 'template_type_display',
            'subject', 'message', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
