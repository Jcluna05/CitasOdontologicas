"""
Vistas para la app appointments.
"""

from datetime import date, timedelta, datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
)

from apps.clinic.models import Clinic, Professional, Schedule
from apps.patients.models import PatientEvent

from .models import Appointment, ProcedureType, AppointmentStatusLog
from .forms import (
    AppointmentForm, AppointmentQuickForm, AppointmentStatusForm,
    AppointmentCancelForm, AppointmentRescheduleForm,
    ProcedureTypeForm, AppointmentFilterForm
)


# Appointment Views
class AppointmentListView(LoginRequiredMixin, ListView):
    """Lista/Agenda de citas."""

    model = Appointment
    template_name = 'appointments/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'patient', 'professional__user', 'procedure_type'
        )

        # Filtros
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        professional = self.request.GET.get('professional')
        status = self.request.GET.get('status')
        procedure_type = self.request.GET.get('procedure_type')

        # Por defecto, mostrar citas de hoy en adelante
        if not date_from and not date_to:
            today = timezone.now().date()
            queryset = queryset.filter(date__gte=today)

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if professional:
            queryset = queryset.filter(professional_id=professional)
        if status:
            queryset = queryset.filter(status=status)
        if procedure_type:
            queryset = queryset.filter(procedure_type_id=procedure_type)

        # Si es profesional, solo ver sus citas
        if self.request.user.is_professional:
            queryset = queryset.filter(professional__user=self.request.user)

        return queryset.order_by('date', 'start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = AppointmentFilterForm(self.request.GET)
        context['today'] = timezone.now().date()
        return context


class AppointmentDayView(LoginRequiredMixin, TemplateView):
    """Vista de agenda por día."""

    template_name = 'appointments/appointment_day.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener fecha del parámetro o usar hoy
        date_str = self.request.GET.get('date')
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = timezone.now().date()
        else:
            selected_date = timezone.now().date()

        context['selected_date'] = selected_date
        context['prev_date'] = selected_date - timedelta(days=1)
        context['next_date'] = selected_date + timedelta(days=1)

        # Obtener citas del día
        appointments = Appointment.objects.filter(
            date=selected_date
        ).select_related(
            'patient', 'professional__user', 'procedure_type'
        ).order_by('start_time')

        # Si es profesional, solo sus citas
        professional_filter = self.request.GET.get('professional')
        if self.request.user.is_professional:
            appointments = appointments.filter(professional__user=self.request.user)
        elif professional_filter:
            appointments = appointments.filter(professional_id=professional_filter)

        context['appointments'] = appointments
        context['professionals'] = Professional.objects.filter(is_active=True)

        # Estadísticas del día
        context['total_count'] = appointments.count()
        context['pending_count'] = appointments.filter(status=Appointment.Status.PENDING).count()
        context['confirmed_count'] = appointments.filter(status=Appointment.Status.CONFIRMED).count()

        return context


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    """Detalle de una cita."""

    model = Appointment
    template_name = 'appointments/appointment_detail.html'
    context_object_name = 'appointment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_logs'] = self.object.status_logs.all()[:10]
        context['cancel_form'] = AppointmentCancelForm()
        context['reschedule_form'] = AppointmentRescheduleForm()
        context['whatsapp_message'] = self.object.get_whatsapp_message()
        return context


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    """Crear una cita."""

    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'

    def get_success_url(self):
        return reverse_lazy('appointments:appointment_detail', kwargs={'pk': self.object.pk})

    def get_initial(self):
        initial = super().get_initial()
        # Pre-llenar fecha y hora si vienen en la URL
        date_str = self.request.GET.get('date')
        time_str = self.request.GET.get('time')
        professional_id = self.request.GET.get('professional')
        patient_id = self.request.GET.get('patient')

        if date_str:
            try:
                initial['date'] = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        if time_str:
            try:
                initial['start_time'] = datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                pass
        if professional_id:
            initial['professional'] = professional_id
        if patient_id:
            initial['patient'] = patient_id

        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.clinic = Clinic.get_default()
        form.instance._changed_by = self.request.user
        messages.success(self.request, 'Cita creada exitosamente.')
        return super().form_valid(form)


class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    """Editar una cita."""

    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'

    def get_success_url(self):
        return reverse_lazy('appointments:appointment_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance._changed_by = self.request.user
        messages.success(self.request, 'Cita actualizada exitosamente.')
        return super().form_valid(form)


class AppointmentDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar una cita."""

    model = Appointment
    template_name = 'appointments/appointment_confirm_delete.html'
    success_url = reverse_lazy('appointments:appointment_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cita eliminada exitosamente.')
        return super().form_valid(form)


class AppointmentConfirmView(LoginRequiredMixin, View):
    """Confirmar una cita."""

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        appointment._changed_by = request.user

        if appointment.confirm():
            messages.success(request, 'Cita confirmada exitosamente.')
        else:
            messages.error(request, 'No se pudo confirmar la cita.')

        return redirect('appointments:appointment_detail', pk=pk)


class AppointmentCancelView(LoginRequiredMixin, View):
    """Cancelar una cita."""

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        form = AppointmentCancelForm(request.POST)

        if form.is_valid():
            reason = form.cleaned_data['cancellation_reason']
            appointment._changed_by = request.user

            if appointment.cancel(reason):
                messages.success(request, 'Cita cancelada exitosamente.')
            else:
                messages.error(request, 'No se pudo cancelar la cita.')
        else:
            messages.error(request, 'Por favor indique el motivo de la cancelación.')

        return redirect('appointments:appointment_detail', pk=pk)


class AppointmentAttendedView(LoginRequiredMixin, View):
    """Marcar cita como atendida."""

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        appointment._changed_by = request.user

        if appointment.mark_attended():
            messages.success(request, 'Cita marcada como atendida.')
        else:
            messages.error(request, 'No se pudo marcar la cita como atendida.')

        return redirect('appointments:appointment_detail', pk=pk)


class AppointmentNoShowView(LoginRequiredMixin, View):
    """Marcar cita como no asistió."""

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        appointment._changed_by = request.user

        if appointment.mark_no_show():
            # Registrar evento en el paciente
            PatientEvent.objects.create(
                patient=appointment.patient,
                event_type=PatientEvent.EventType.NO_SHOW,
                description=f'No asistió a la cita del {appointment.date}',
                created_by=request.user,
            )
            messages.warning(
                request,
                f'Cita marcada como "No asistió". '
                f'Inasistencias del paciente: {appointment.patient.no_show_count}'
            )
        else:
            messages.error(request, 'No se pudo actualizar el estado de la cita.')

        return redirect('appointments:appointment_detail', pk=pk)


class AppointmentRescheduleView(LoginRequiredMixin, View):
    """Reprogramar una cita."""

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        form = AppointmentRescheduleForm(request.POST)

        if form.is_valid():
            old_date = appointment.date
            old_time = appointment.start_time

            # Cancelar la cita actual
            reason = form.cleaned_data.get('reason', 'Reprogramación')
            appointment._changed_by = request.user
            appointment.cancel(f'Reprogramación: {reason}')

            # Crear nueva cita
            new_appointment = Appointment.objects.create(
                patient=appointment.patient,
                professional=appointment.professional,
                procedure_type=appointment.procedure_type,
                clinic=appointment.clinic,
                date=form.cleaned_data['new_date'],
                start_time=form.cleaned_data['new_start_time'],
                notes=f'Reprogramada desde {old_date} {old_time}. {appointment.notes}',
                created_by=request.user,
            )

            messages.success(
                request,
                f'Cita reprogramada de {old_date} a {new_appointment.date}.'
            )
            return redirect('appointments:appointment_detail', pk=new_appointment.pk)
        else:
            messages.error(request, 'Error al reprogramar la cita.')
            return redirect('appointments:appointment_detail', pk=pk)


# Procedure Type Views
class ProcedureTypeListView(LoginRequiredMixin, ListView):
    """Lista de tipos de procedimientos."""

    model = ProcedureType
    template_name = 'appointments/proceduretype_list.html'
    context_object_name = 'procedures'


class ProcedureTypeCreateView(LoginRequiredMixin, CreateView):
    """Crear un tipo de procedimiento."""

    model = ProcedureType
    form_class = ProcedureTypeForm
    template_name = 'appointments/proceduretype_form.html'
    success_url = reverse_lazy('appointments:proceduretype_list')

    def form_valid(self, form):
        messages.success(self.request, 'Procedimiento creado exitosamente.')
        return super().form_valid(form)


class ProcedureTypeUpdateView(LoginRequiredMixin, UpdateView):
    """Editar un tipo de procedimiento."""

    model = ProcedureType
    form_class = ProcedureTypeForm
    template_name = 'appointments/proceduretype_form.html'
    success_url = reverse_lazy('appointments:proceduretype_list')

    def form_valid(self, form):
        messages.success(self.request, 'Procedimiento actualizado exitosamente.')
        return super().form_valid(form)


class ProcedureTypeDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar un tipo de procedimiento."""

    model = ProcedureType
    template_name = 'appointments/proceduretype_confirm_delete.html'
    success_url = reverse_lazy('appointments:proceduretype_list')

    def form_valid(self, form):
        messages.success(self.request, 'Procedimiento eliminado exitosamente.')
        return super().form_valid(form)


# Availability Views
class AvailabilityView(LoginRequiredMixin, TemplateView):
    """Vista de disponibilidad inteligente."""

    template_name = 'appointments/availability.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Parámetros
        date_str = self.request.GET.get('date')
        professional_id = self.request.GET.get('professional')
        procedure_id = self.request.GET.get('procedure')

        if date_str:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                selected_date = timezone.now().date()
        else:
            selected_date = timezone.now().date()

        context['selected_date'] = selected_date
        context['professionals'] = Professional.objects.filter(is_active=True)
        context['procedures'] = ProcedureType.objects.filter(is_active=True)

        # Calcular slots disponibles
        if professional_id and procedure_id:
            try:
                professional = Professional.objects.get(pk=professional_id)
                procedure = ProcedureType.objects.get(pk=procedure_id)
                context['available_slots'] = self.get_available_slots(
                    selected_date, professional, procedure.duration_minutes
                )
                context['selected_professional'] = professional
                context['selected_procedure'] = procedure
            except (Professional.DoesNotExist, ProcedureType.DoesNotExist):
                context['available_slots'] = []
        else:
            context['available_slots'] = []

        return context

    def get_available_slots(self, date, professional, duration_minutes):
        """Calcular slots disponibles."""
        weekday = date.weekday()

        # Obtener horarios del profesional para este día
        schedules = Schedule.objects.filter(
            Q(professional=professional) | Q(professional__isnull=True, clinic=professional.clinic),
            weekday=weekday,
            is_active=True,
        ).order_by('-professional')  # Priorizar horario del profesional

        if not schedules.exists():
            return []

        schedule = schedules.first()

        # Obtener citas existentes
        existing_appointments = Appointment.objects.filter(
            professional=professional,
            date=date,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).order_by('start_time')

        # Generar slots
        slots = []
        current_time = datetime.combine(date, schedule.start_time)
        end_time = datetime.combine(date, schedule.end_time)
        slot_duration = timedelta(minutes=duration_minutes)

        while current_time + slot_duration <= end_time:
            slot_start = current_time.time()
            slot_end = (current_time + slot_duration).time()

            # Verificar si hay conflicto
            is_available = True
            for apt in existing_appointments:
                if slot_start < apt.end_time and slot_end > apt.start_time:
                    is_available = False
                    break

            if is_available:
                slots.append({
                    'start_time': slot_start,
                    'end_time': slot_end,
                    'formatted': f'{slot_start.strftime("%H:%M")} - {slot_end.strftime("%H:%M")}'
                })

            current_time += timedelta(minutes=30)  # Incremento de 30 min

        return slots


class AppointmentCopyMessageView(LoginRequiredMixin, View):
    """Obtener el mensaje para copiar (AJAX)."""

    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        return JsonResponse({
            'message': appointment.get_whatsapp_message()
        })
