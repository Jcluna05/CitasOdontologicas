"""
Serializers para la API de appointments.
"""

from rest_framework import serializers

from apps.clinic.serializers import ProfessionalListSerializer
from apps.patients.serializers import PatientListSerializer

from .models import Appointment, ProcedureType, AppointmentStatusLog


class ProcedureTypeSerializer(serializers.ModelSerializer):
    """Serializer para el modelo ProcedureType."""

    class Meta:
        model = ProcedureType
        fields = [
            'id', 'name', 'description', 'duration_minutes',
            'color', 'requires_confirmation', 'is_active', 'order'
        ]
        read_only_fields = ['id']


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Appointment."""

    patient_data = PatientListSerializer(source='patient', read_only=True)
    professional_data = ProfessionalListSerializer(source='professional', read_only=True)
    procedure_data = ProcedureTypeSerializer(source='procedure_type', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_color = serializers.CharField(read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)
    is_today = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)
    can_be_confirmed = serializers.BooleanField(read_only=True)
    whatsapp_message = serializers.CharField(
        source='get_whatsapp_message',
        read_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_data', 'professional', 'professional_data',
            'procedure_type', 'procedure_data', 'clinic',
            'date', 'start_time', 'end_time', 'duration_minutes',
            'status', 'status_display', 'status_color',
            'notes', 'cancellation_reason', 'cancelled_at',
            'reminder_sent', 'reminder_sent_at', 'confirmed_at',
            'is_today', 'is_past', 'can_be_cancelled', 'can_be_confirmed',
            'whatsapp_message',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'cancelled_at', 'reminder_sent', 'reminder_sent_at',
            'confirmed_at', 'created_at', 'updated_at'
        ]


class AppointmentListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de citas."""

    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    professional_name = serializers.CharField(source='professional.full_name', read_only=True)
    procedure_name = serializers.CharField(source='procedure_type.name', read_only=True)
    procedure_color = serializers.CharField(source='procedure_type.color', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_color = serializers.CharField(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'professional', 'professional_name',
            'procedure_type', 'procedure_name', 'procedure_color',
            'date', 'start_time', 'end_time',
            'status', 'status_display', 'status_color'
        ]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear citas."""

    class Meta:
        model = Appointment
        fields = [
            'patient', 'professional', 'procedure_type', 'clinic',
            'date', 'start_time', 'end_time', 'notes'
        ]

    def validate(self, data):
        # Auto-calcular end_time si no está proporcionado
        if 'start_time' in data and 'procedure_type' in data:
            if not data.get('end_time'):
                from datetime import datetime, timedelta, date
                start_datetime = datetime.combine(date.today(), data['start_time'])
                duration = data['procedure_type'].duration_minutes
                end_datetime = start_datetime + timedelta(minutes=duration)
                data['end_time'] = end_datetime.time()
        return data


class AppointmentStatusLogSerializer(serializers.ModelSerializer):
    """Serializer para logs de estado."""

    previous_status_display = serializers.CharField(
        source='get_previous_status_display',
        read_only=True
    )
    new_status_display = serializers.CharField(
        source='get_new_status_display',
        read_only=True
    )
    changed_by_name = serializers.CharField(
        source='changed_by.get_full_name',
        read_only=True
    )

    class Meta:
        model = AppointmentStatusLog
        fields = [
            'id', 'appointment', 'previous_status', 'previous_status_display',
            'new_status', 'new_status_display', 'changed_by', 'changed_by_name',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AvailableSlotSerializer(serializers.Serializer):
    """Serializer para slots disponibles."""

    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    formatted = serializers.CharField()
