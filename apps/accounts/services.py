"""
Servicios para el dashboard y lógica de negocio de accounts.
"""

from datetime import datetime, timedelta, time
from django.db.models import Count, Q, Prefetch
from django.utils import timezone

from apps.appointments.models import Appointment, ProcedureType
from apps.patients.models import Patient
from apps.clinic.models import Professional, Schedule, Clinic


class DashboardService:
    """Servicio para obtener datos del dashboard con queries optimizadas."""

    def __init__(self, user):
        self.user = user
        self.today = timezone.now().date()
        self.now = timezone.now()

    def get_today_stats(self):
        """Obtener KPIs del día actual."""
        base_query = Appointment.objects.filter(date=self.today)

        if self.user.is_professional:
            base_query = base_query.filter(professional__user=self.user)

        stats = base_query.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status=Appointment.Status.PENDING)),
            confirmed=Count('id', filter=Q(status=Appointment.Status.CONFIRMED)),
            attended=Count('id', filter=Q(status=Appointment.Status.ATTENDED)),
            cancelled=Count('id', filter=Q(status=Appointment.Status.CANCELLED)),
            no_show=Count('id', filter=Q(status=Appointment.Status.NO_SHOW)),
        )

        return stats

    def get_today_appointments(self, limit=10):
        """Obtener citas de hoy con datos relacionados optimizados."""
        queryset = Appointment.objects.filter(
            date=self.today
        ).select_related(
            'patient', 'professional', 'professional__user', 'procedure_type'
        ).order_by('start_time')

        if self.user.is_professional:
            queryset = queryset.filter(professional__user=self.user)

        return queryset[:limit]

    def get_upcoming_appointments(self, days=7, limit=5):
        """Obtener próximas citas."""
        end_date = self.today + timedelta(days=days)

        queryset = Appointment.objects.filter(
            date__gt=self.today,
            date__lte=end_date,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).select_related(
            'patient', 'professional', 'professional__user', 'procedure_type'
        ).order_by('date', 'start_time')

        if self.user.is_professional:
            queryset = queryset.filter(professional__user=self.user)

        return queryset[:limit]

    def get_smart_alerts(self):
        """Obtener alertas inteligentes."""
        alerts = []
        tomorrow = self.today + timedelta(days=1)

        # 1. Pacientes con 2+ inasistencias que tienen citas próximas
        patients_with_no_shows = Patient.objects.filter(
            no_show_count__gte=2,
            appointments__date__gte=self.today,
            appointments__status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).distinct()[:5]

        for patient in patients_with_no_shows:
            alerts.append({
                'type': 'warning',
                'icon': 'exclamation-triangle',
                'title': f'{patient.full_name}',
                'message': f'{patient.no_show_count} inasistencias - requiere anticipo',
                'action_url': f'/patients/{patient.pk}/',
                'action_text': 'Ver paciente'
            })

        # 2. Citas sin confirmar a menos de 24h
        unconfirmed_soon = Appointment.objects.filter(
            date__lte=tomorrow,
            date__gte=self.today,
            status=Appointment.Status.PENDING
        ).select_related('patient', 'professional__user')[:5]

        for apt in unconfirmed_soon:
            time_str = "hoy" if apt.date == self.today else "mañana"
            alerts.append({
                'type': 'info',
                'icon': 'clock',
                'title': f'Cita sin confirmar ({time_str})',
                'message': f'{apt.patient.full_name} - {apt.start_time.strftime("%H:%M")}',
                'action_url': f'/appointments/{apt.pk}/',
                'action_text': 'Confirmar'
            })

        # 3. Pacientes con alertas médicas que tienen cita hoy
        patients_with_alerts_today = Appointment.objects.filter(
            date=self.today,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).filter(
            Q(patient__has_acute_pain=True) |
            Q(patient__has_allergies=True) |
            Q(patient__has_anxiety=True) |
            Q(patient__is_child=True) |
            Q(patient__is_elderly=True)
        ).select_related('patient')[:5]

        for apt in patients_with_alerts_today:
            alert_types = []
            if apt.patient.has_acute_pain:
                alert_types.append('🔴 Dolor agudo')
            if apt.patient.has_allergies:
                alert_types.append('⚠️ Alergias')
            if apt.patient.has_anxiety:
                alert_types.append('😰 Ansiedad')
            if apt.patient.is_child:
                alert_types.append('👶 Niño')
            if apt.patient.is_elderly:
                alert_types.append('👴 Adulto mayor')

            alerts.append({
                'type': 'danger' if apt.patient.has_acute_pain else 'warning',
                'icon': 'heart-pulse',
                'title': f'{apt.patient.full_name} - {apt.start_time.strftime("%H:%M")}',
                'message': ' | '.join(alert_types),
                'action_url': f'/patients/{apt.patient.pk}/',
                'action_text': 'Ver ficha'
            })

        return alerts[:8]  # Limitar a 8 alertas

    def get_available_slots(self, procedure_id=None, days=2, limit=5):
        """Obtener slots disponibles para agendar."""
        slots = []

        # Obtener duración del procedimiento o usar default
        duration_minutes = 30
        if procedure_id:
            try:
                procedure = ProcedureType.objects.get(pk=procedure_id)
                duration_minutes = procedure.duration_minutes
            except ProcedureType.DoesNotExist:
                pass

        # Obtener profesionales activos
        professionals = Professional.objects.filter(
            is_active=True
        ).select_related('user')

        for day_offset in range(days + 1):
            check_date = self.today + timedelta(days=day_offset)
            weekday = check_date.weekday()

            for professional in professionals:
                # Obtener horarios del profesional para este día
                schedules = Schedule.objects.filter(
                    professional=professional,
                    weekday=weekday,
                    is_active=True
                )

                for schedule in schedules:
                    # Generar slots disponibles
                    current_time = datetime.combine(check_date, schedule.start_time)
                    end_time = datetime.combine(check_date, schedule.end_time)

                    # Si es hoy, empezar desde ahora + 30 min
                    if check_date == self.today:
                        min_time = timezone.now() + timedelta(minutes=30)
                        if current_time < min_time:
                            current_time = min_time
                            # Redondear a la media hora más cercana
                            current_time = current_time.replace(
                                minute=30 if current_time.minute < 30 else 0,
                                second=0,
                                microsecond=0
                            )
                            if current_time.minute == 0:
                                current_time = current_time + timedelta(hours=1)

                    while current_time + timedelta(minutes=duration_minutes) <= end_time:
                        slot_start = current_time.time()
                        slot_end = (current_time + timedelta(minutes=duration_minutes)).time()

                        # Verificar si el slot está ocupado
                        is_occupied = Appointment.objects.filter(
                            professional=professional,
                            date=check_date,
                            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
                        ).filter(
                            Q(start_time__lt=slot_end, end_time__gt=slot_start)
                        ).exists()

                        if not is_occupied:
                            slots.append({
                                'date': check_date,
                                'date_display': 'Hoy' if check_date == self.today else (
                                    'Mañana' if check_date == self.today + timedelta(days=1) else
                                    check_date.strftime('%d/%m')
                                ),
                                'start_time': slot_start,
                                'end_time': slot_end,
                                'professional': professional,
                                'professional_id': professional.pk,
                            })

                            if len(slots) >= limit:
                                return slots

                        current_time = current_time + timedelta(minutes=duration_minutes)

        return slots

    def get_weekly_stats(self):
        """Obtener estadísticas de la semana."""
        week_start = self.today - timedelta(days=self.today.weekday())
        week_end = week_start + timedelta(days=6)

        base_query = Appointment.objects.filter(
            date__gte=week_start,
            date__lte=week_end
        )

        if self.user.is_professional:
            base_query = base_query.filter(professional__user=self.user)

        # Estadísticas generales
        stats = base_query.aggregate(
            total=Count('id'),
            attended=Count('id', filter=Q(status=Appointment.Status.ATTENDED)),
            no_show=Count('id', filter=Q(status=Appointment.Status.NO_SHOW)),
            cancelled=Count('id', filter=Q(status=Appointment.Status.CANCELLED)),
        )

        # Calcular porcentaje de inasistencias
        total_finished = stats['attended'] + stats['no_show']
        stats['no_show_rate'] = round(
            (stats['no_show'] / total_finished * 100) if total_finished > 0 else 0, 1
        )

        # Procedimientos más frecuentes
        procedures = base_query.values(
            'procedure_type__name', 'procedure_type__color'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        stats['top_procedures'] = list(procedures)

        # Carga por profesional (solo para admin/recepción)
        if not self.user.is_professional:
            professionals_load = base_query.values(
                'professional__user__first_name',
                'professional__user__last_name',
                'professional__color'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:5]

            stats['professionals_load'] = list(professionals_load)

        return stats

    def get_gaps_in_schedule(self, min_gap_minutes=60):
        """Detectar huecos libres en la agenda de hoy."""
        gaps = []

        professionals = Professional.objects.filter(is_active=True).select_related('user')

        for professional in professionals:
            # Obtener citas de hoy del profesional
            appointments = Appointment.objects.filter(
                professional=professional,
                date=self.today,
                status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED, Appointment.Status.ATTENDED]
            ).order_by('start_time')

            if not appointments.exists():
                continue

            # Obtener horario del profesional
            schedules = Schedule.objects.filter(
                professional=professional,
                weekday=self.today.weekday(),
                is_active=True
            ).order_by('start_time')

            for schedule in schedules:
                schedule_start = datetime.combine(self.today, schedule.start_time)
                schedule_end = datetime.combine(self.today, schedule.end_time)

                prev_end = schedule_start

                for apt in appointments:
                    apt_start = datetime.combine(self.today, apt.start_time)
                    apt_end = datetime.combine(self.today, apt.end_time)

                    # Si hay hueco antes de esta cita
                    if apt_start > prev_end:
                        gap_minutes = (apt_start - prev_end).total_seconds() / 60
                        if gap_minutes >= min_gap_minutes:
                            gaps.append({
                                'professional': professional,
                                'start_time': prev_end.time(),
                                'end_time': apt_start.time(),
                                'duration_minutes': int(gap_minutes)
                            })

                    prev_end = max(prev_end, apt_end)

                # Verificar hueco al final del horario
                if schedule_end > prev_end:
                    gap_minutes = (schedule_end - prev_end).total_seconds() / 60
                    if gap_minutes >= min_gap_minutes:
                        gaps.append({
                            'professional': professional,
                            'start_time': prev_end.time(),
                            'end_time': schedule_end.time(),
                            'duration_minutes': int(gap_minutes)
                        })

        return gaps[:5]  # Limitar a 5 huecos
