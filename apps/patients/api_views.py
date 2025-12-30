"""
API Views para la app patients.
"""

from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsReceptionOrAdmin, ReadOnlyForProfessional

from .models import Patient, PatientEvent
from .serializers import (
    PatientSerializer,
    PatientListSerializer,
    PatientCreateSerializer,
    PatientEventSerializer,
)


class PatientViewSet(viewsets.ModelViewSet):
    """ViewSet para pacientes."""

    queryset = Patient.objects.all()
    permission_classes = [IsAuthenticated, ReadOnlyForProfessional]

    def get_serializer_class(self):
        if self.action == 'list':
            return PatientListSerializer
        if self.action == 'create':
            return PatientCreateSerializer
        return PatientSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Búsqueda
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(medical_record_number__icontains=search) |
                Q(phone__icontains=search)
            )

        # Filtro por estado
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filtro por alertas
        with_warnings = self.request.query_params.get('with_warnings')
        if with_warnings == 'true':
            queryset = queryset.filter(
                Q(has_anxiety=True) |
                Q(has_allergies=True) |
                Q(has_acute_pain=True) |
                Q(no_show_count__gte=1)
            )

        return queryset

    @action(detail=True, methods=['post'])
    def register_no_show(self, request, pk=None):
        """Registrar una inasistencia."""
        patient = self.get_object()
        patient.register_no_show()
        return Response({
            'message': 'Inasistencia registrada.',
            'no_show_count': patient.no_show_count,
            'requires_advance_payment': patient.requires_advance_payment,
        })

    @action(detail=True, methods=['post'])
    def reset_no_shows(self, request, pk=None):
        """Reiniciar el contador de inasistencias."""
        patient = self.get_object()
        patient.reset_no_shows()
        return Response({
            'message': 'Contador de inasistencias reiniciado.',
            'no_show_count': patient.no_show_count,
        })

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Obtener los eventos de un paciente."""
        patient = self.get_object()
        events = patient.events.all()
        serializer = PatientEventSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_event(self, request, pk=None):
        """Agregar un evento al paciente."""
        patient = self.get_object()
        serializer = PatientEventSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(patient=patient, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        """Obtener las citas de un paciente."""
        from apps.appointments.models import Appointment
        from apps.appointments.serializers import AppointmentListSerializer

        patient = self.get_object()
        appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-start_time')
        serializer = AppointmentListSerializer(appointments, many=True)
        return Response(serializer.data)
