"""
API Views para la app appointments.
"""

from datetime import datetime, timedelta

from django.db.models import Q, Count
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsReceptionOrAdmin, ReadOnlyForProfessional
from apps.clinic.models import Professional, Schedule

from .models import Appointment, ProcedureType, AppointmentStatusLog
from .serializers import (
    AppointmentSerializer,
    AppointmentListSerializer,
    AppointmentCreateSerializer,
    ProcedureTypeSerializer,
    AppointmentStatusLogSerializer,
    AvailableSlotSerializer,
)


class ProcedureTypeViewSet(viewsets.ModelViewSet):
    """ViewSet para tipos de procedimientos."""

    queryset = ProcedureType.objects.all()
    serializer_class = ProcedureTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset.order_by('order', 'name')


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet para citas."""

    queryset = Appointment.objects.select_related(
        'patient', 'professional__user', 'procedure_type', 'clinic'
    ).all()
    permission_classes = [IsAuthenticated, ReadOnlyForProfessional]

    def get_serializer_class(self):
        if self.action == 'list':
            return AppointmentListSerializer
        if self.action == 'create':
            return AppointmentCreateSerializer
        return AppointmentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtros
        date = self.request.query_params.get('date')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        professional = self.request.query_params.get('professional')
        patient = self.request.query_params.get('patient')
        status_filter = self.request.query_params.get('status')

        if date:
            queryset = queryset.filter(date=date)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if professional:
            queryset = queryset.filter(professional_id=professional)
        if patient:
            queryset = queryset.filter(patient_id=patient)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Si es profesional, solo sus citas
        if self.request.user.is_professional:
            queryset = queryset.filter(professional__user=self.request.user)

        return queryset.order_by('date', 'start_time')

    def perform_create(self, serializer):
        from apps.clinic.models import Clinic
        serializer.save(
            created_by=self.request.user,
            clinic=Clinic.get_default(),
        )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirmar una cita."""
        appointment = self.get_object()
        appointment._changed_by = request.user

        if appointment.confirm():
            return Response({
                'message': 'Cita confirmada exitosamente.',
                'status': appointment.status,
            })
        return Response(
            {'error': 'No se pudo confirmar la cita.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar una cita."""
        appointment = self.get_object()
        reason = request.data.get('reason', '')
        appointment._changed_by = request.user

        if appointment.cancel(reason):
            return Response({
                'message': 'Cita cancelada exitosamente.',
                'status': appointment.status,
            })
        return Response(
            {'error': 'No se pudo cancelar la cita.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def attended(self, request, pk=None):
        """Marcar cita como atendida."""
        appointment = self.get_object()
        appointment._changed_by = request.user

        if appointment.mark_attended():
            return Response({
                'message': 'Cita marcada como atendida.',
                'status': appointment.status,
            })
        return Response(
            {'error': 'No se pudo actualizar el estado.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def no_show(self, request, pk=None):
        """Marcar cita como no asistió."""
        appointment = self.get_object()
        appointment._changed_by = request.user

        if appointment.mark_no_show():
            return Response({
                'message': 'Cita marcada como "No asistió".',
                'status': appointment.status,
                'patient_no_show_count': appointment.patient.no_show_count,
            })
        return Response(
            {'error': 'No se pudo actualizar el estado.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['get'])
    def status_logs(self, request, pk=None):
        """Obtener los logs de estado de una cita."""
        appointment = self.get_object()
        logs = appointment.status_logs.all()
        serializer = AppointmentStatusLogSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def whatsapp_message(self, request, pk=None):
        """Obtener el mensaje formateado para WhatsApp."""
        appointment = self.get_object()
        return Response({
            'message': appointment.get_whatsapp_message()
        })

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Obtener las citas de hoy."""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(date=today)
        serializer = AppointmentListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Obtener las próximas citas (próximos 7 días)."""
        today = timezone.now().date()
        week_later = today + timedelta(days=7)
        queryset = self.get_queryset().filter(
            date__gte=today,
            date__lte=week_later,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        )
        serializer = AppointmentListSerializer(queryset, many=True)
        return Response(serializer.data)


class AvailabilityAPIView(APIView):
    """API para consultar disponibilidad."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_str = request.query_params.get('date')
        professional_id = request.query_params.get('professional')
        duration = request.query_params.get('duration', 30)

        if not date_str or not professional_id:
            return Response(
                {'error': 'Se requieren los parámetros date y professional.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            professional = Professional.objects.get(pk=professional_id)
            duration = int(duration)
        except (ValueError, Professional.DoesNotExist):
            return Response(
                {'error': 'Parámetros inválidos.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        slots = self.get_available_slots(selected_date, professional, duration)
        serializer = AvailableSlotSerializer(slots, many=True)
        return Response(serializer.data)

    def get_available_slots(self, date, professional, duration_minutes):
        """Calcular slots disponibles."""
        weekday = date.weekday()

        # Obtener horarios
        schedules = Schedule.objects.filter(
            Q(professional=professional) | Q(professional__isnull=True),
            weekday=weekday,
            is_active=True,
        ).order_by('-professional')

        if not schedules.exists():
            return []

        schedule = schedules.first()

        # Obtener citas existentes
        existing = Appointment.objects.filter(
            professional=professional,
            date=date,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).order_by('start_time')

        # Generar slots
        slots = []
        current = datetime.combine(date, schedule.start_time)
        end = datetime.combine(date, schedule.end_time)
        duration = timedelta(minutes=duration_minutes)

        while current + duration <= end:
            slot_start = current.time()
            slot_end = (current + duration).time()

            is_available = True
            for apt in existing:
                if slot_start < apt.end_time and slot_end > apt.start_time:
                    is_available = False
                    break

            if is_available:
                slots.append({
                    'start_time': slot_start,
                    'end_time': slot_end,
                    'formatted': f'{slot_start.strftime("%H:%M")} - {slot_end.strftime("%H:%M")}'
                })

            current += timedelta(minutes=30)

        return slots


class DashboardStatsAPIView(APIView):
    """API para estadísticas del dashboard."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        # Estadísticas de hoy
        today_appointments = Appointment.objects.filter(date=today)
        today_stats = {
            'total': today_appointments.count(),
            'pending': today_appointments.filter(status=Appointment.Status.PENDING).count(),
            'confirmed': today_appointments.filter(status=Appointment.Status.CONFIRMED).count(),
            'attended': today_appointments.filter(status=Appointment.Status.ATTENDED).count(),
            'cancelled': today_appointments.filter(status=Appointment.Status.CANCELLED).count(),
            'no_show': today_appointments.filter(status=Appointment.Status.NO_SHOW).count(),
        }

        # Estadísticas de la semana
        week_appointments = Appointment.objects.filter(
            date__gte=week_start,
            date__lte=today
        )
        week_total = week_appointments.count()
        week_cancelled = week_appointments.filter(status=Appointment.Status.CANCELLED).count()
        week_no_show = week_appointments.filter(status=Appointment.Status.NO_SHOW).count()

        week_stats = {
            'total': week_total,
            'cancelled_pct': round((week_cancelled / week_total * 100) if week_total > 0 else 0, 1),
            'no_show_pct': round((week_no_show / week_total * 100) if week_total > 0 else 0, 1),
        }

        # Procedimientos más frecuentes
        top_procedures = Appointment.objects.filter(
            date__gte=month_start
        ).values(
            'procedure_type__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        # Pacientes con más inasistencias
        from apps.patients.models import Patient
        top_no_shows = Patient.objects.filter(
            no_show_count__gt=0
        ).order_by('-no_show_count')[:5].values(
            'id', 'first_name', 'last_name', 'no_show_count'
        )

        return Response({
            'today': today_stats,
            'week': week_stats,
            'top_procedures': list(top_procedures),
            'top_no_shows': list(top_no_shows),
        })
