"""
Serializers para la API de patients.
"""

from rest_framework import serializers

from .models import Patient, PatientEvent


class PatientSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Patient."""

    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    age_display = serializers.CharField(read_only=True)
    triage_alerts = serializers.ListField(read_only=True)
    has_warnings = serializers.BooleanField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id', 'medical_record_number', 'first_name', 'last_name',
            'full_name', 'birth_date', 'age', 'age_display', 'gender',
            'phone', 'whatsapp', 'email', 'address',
            'has_anxiety', 'has_allergies', 'allergies_detail',
            'has_acute_pain', 'is_child', 'is_elderly',
            'medical_notes', 'observations',
            'no_show_count', 'requires_advance_payment',
            'status', 'has_warnings', 'triage_alerts',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'no_show_count', 'requires_advance_payment',
            'created_at', 'updated_at'
        ]


class PatientListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados."""

    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    has_warnings = serializers.BooleanField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id', 'medical_record_number', 'full_name',
            'phone', 'age', 'status', 'has_warnings', 'no_show_count'
        ]


class PatientCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pacientes."""

    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'birth_date', 'gender',
            'phone', 'whatsapp', 'email', 'address',
            'has_anxiety', 'has_allergies', 'allergies_detail',
            'has_acute_pain', 'is_child', 'is_elderly',
            'medical_notes', 'observations'
        ]

    def create(self, validated_data):
        validated_data['medical_record_number'] = Patient.generate_medical_record_number()
        return super().create(validated_data)


class PatientEventSerializer(serializers.ModelSerializer):
    """Serializer para eventos de pacientes."""

    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )

    class Meta:
        model = PatientEvent
        fields = [
            'id', 'patient', 'event_type', 'description',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
