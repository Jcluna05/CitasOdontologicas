"""
Vistas para la app patients.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)

from .models import Patient, PatientEvent
from .forms import (
    PatientForm, PatientQuickForm, PatientTriageForm,
    PatientEventForm, PatientSearchForm
)


class PatientListView(LoginRequiredMixin, ListView):
    """Lista de pacientes."""

    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Búsqueda
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(medical_record_number__icontains=q) |
                Q(phone__icontains=q) |
                Q(email__icontains=q)
            )

        # Filtro por estado
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PatientSearchForm(self.request.GET)
        return context


class PatientDetailView(LoginRequiredMixin, DetailView):
    """Detalle de un paciente."""

    model = Patient
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = self.object.events.all()[:10]
        context['event_form'] = PatientEventForm()

        # Últimas citas
        from apps.appointments.models import Appointment
        context['appointments'] = Appointment.objects.filter(
            patient=self.object
        ).order_by('-date', '-start_time')[:10]

        return context


class PatientCreateView(LoginRequiredMixin, CreateView):
    """Crear un paciente."""

    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'

    def get_success_url(self):
        return reverse_lazy('patients:patient_detail', kwargs={'pk': self.object.pk})

    def get_initial(self):
        initial = super().get_initial()
        initial['medical_record_number'] = Patient.generate_medical_record_number()
        return initial

    def form_valid(self, form):
        from apps.clinic.models import Clinic
        form.instance.clinic = Clinic.get_default()
        messages.success(self.request, 'Paciente creado exitosamente.')
        return super().form_valid(form)


class PatientUpdateView(LoginRequiredMixin, UpdateView):
    """Editar un paciente."""

    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'

    def get_success_url(self):
        return reverse_lazy('patients:patient_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Paciente actualizado exitosamente.')
        return super().form_valid(form)


class PatientDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar un paciente."""

    model = Patient
    template_name = 'patients/patient_confirm_delete.html'
    success_url = reverse_lazy('patients:patient_list')

    def form_valid(self, form):
        messages.success(self.request, 'Paciente eliminado exitosamente.')
        return super().form_valid(form)


class PatientTriageUpdateView(LoginRequiredMixin, UpdateView):
    """Actualizar el triage de un paciente."""

    model = Patient
    form_class = PatientTriageForm
    template_name = 'patients/patient_triage_form.html'

    def get_success_url(self):
        return reverse_lazy('patients:patient_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Triage actualizado exitosamente.')
        return super().form_valid(form)


class PatientEventCreateView(LoginRequiredMixin, View):
    """Crear un evento para un paciente."""

    def post(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        form = PatientEventForm(request.POST)

        if form.is_valid():
            event = form.save(commit=False)
            event.patient = patient
            event.created_by = request.user
            event.save()
            messages.success(request, 'Evento registrado exitosamente.')
        else:
            messages.error(request, 'Error al registrar el evento.')

        return redirect('patients:patient_detail', pk=pk)


class PatientSearchAPIView(LoginRequiredMixin, View):
    """API para buscar pacientes (autocomplete)."""

    def get(self, request):
        q = request.GET.get('q', '')
        if len(q) < 2:
            return JsonResponse({'results': []})

        patients = Patient.objects.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(medical_record_number__icontains=q) |
            Q(phone__icontains=q)
        )[:10]

        results = [{
            'id': p.id,
            'text': f'{p.full_name} ({p.medical_record_number})',
            'phone': p.phone,
        } for p in patients]

        return JsonResponse({'results': results})


class PatientQuickCreateView(LoginRequiredMixin, CreateView):
    """Crear paciente rápidamente (modal)."""

    model = Patient
    form_class = PatientQuickForm
    template_name = 'patients/patient_quick_form.html'

    def form_valid(self, form):
        from apps.clinic.models import Clinic
        form.instance.clinic = Clinic.get_default()
        self.object = form.save()

        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'patient': {
                    'id': self.object.id,
                    'name': self.object.full_name,
                    'medical_record_number': self.object.medical_record_number,
                }
            })

        messages.success(self.request, 'Paciente creado exitosamente.')
        return redirect('patients:patient_detail', pk=self.object.pk)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)
