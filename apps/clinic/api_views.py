"""
API Views para la app clinic.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsAdminUser, IsReceptionOrAdmin

from .models import Clinic, Professional, Schedule, MessageTemplate
from .serializers import (
    ClinicSerializer,
    ProfessionalSerializer,
    ProfessionalListSerializer,
    ScheduleSerializer,
    MessageTemplateSerializer,
)


class ClinicViewSet(viewsets.ModelViewSet):
    """ViewSet para el consultorio."""

    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Obtener el consultorio actual (por defecto)."""
        clinic = Clinic.get_default()
        serializer = self.get_serializer(clinic)
        return Response(serializer.data)


class ProfessionalViewSet(viewsets.ModelViewSet):
    """ViewSet para profesionales."""

    queryset = Professional.objects.select_related('user', 'clinic').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ProfessionalListSerializer
        return ProfessionalSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset

    @action(detail=True, methods=['get'])
    def schedules(self, request, pk=None):
        """Obtener los horarios de un profesional."""
        professional = self.get_object()
        schedules = professional.schedules.filter(is_active=True)
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)


class ScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet para horarios."""

    queryset = Schedule.objects.select_related('clinic', 'professional').all()
    serializer_class = ScheduleSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()
        professional = self.request.query_params.get('professional')
        weekday = self.request.query_params.get('weekday')

        if professional:
            queryset = queryset.filter(professional_id=professional)
        if weekday:
            queryset = queryset.filter(weekday=weekday)

        return queryset.filter(is_active=True)


class MessageTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet para plantillas de mensajes."""

    queryset = MessageTemplate.objects.select_related('clinic').all()
    serializer_class = MessageTemplateSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        template_type = self.request.query_params.get('type')
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        return queryset
