"""
Vistas para la app clinic.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)

from apps.accounts.permissions import IsAdminUser

from .models import Clinic, Professional, Schedule, MessageTemplate
from .forms import ClinicForm, ProfessionalForm, ScheduleForm, ScheduleFormSet, MessageTemplateForm


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin que requiere que el usuario sea administrador."""

    def test_func(self):
        return self.request.user.is_admin


# Clinic Views
class ClinicSettingsView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Vista para configuración del consultorio."""

    model = Clinic
    form_class = ClinicForm
    template_name = 'clinic/clinic_settings.html'
    success_url = reverse_lazy('clinic:settings')

    def get_object(self):
        return Clinic.get_default()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic = self.get_object()
        if self.request.POST:
            context['schedule_formset'] = ScheduleFormSet(self.request.POST, instance=clinic)
        else:
            context['schedule_formset'] = ScheduleFormSet(instance=clinic)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        schedule_formset = context['schedule_formset']

        if schedule_formset.is_valid():
            self.object = form.save()
            schedule_formset.instance = self.object
            schedule_formset.save()
            messages.success(self.request, 'Configuración guardada exitosamente.')
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


# Professional Views
class ProfessionalListView(LoginRequiredMixin, ListView):
    """Lista de profesionales."""

    model = Professional
    template_name = 'clinic/professional_list.html'
    context_object_name = 'professionals'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user', 'clinic')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                user__first_name__icontains=search
            ) | queryset.filter(
                user__last_name__icontains=search
            )
        return queryset


class ProfessionalDetailView(LoginRequiredMixin, DetailView):
    """Detalle de un profesional."""

    model = Professional
    template_name = 'clinic/professional_detail.html'
    context_object_name = 'professional'


class ProfessionalCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Crear un profesional."""

    model = Professional
    form_class = ProfessionalForm
    template_name = 'clinic/professional_form.html'
    success_url = reverse_lazy('clinic:professional_list')

    def form_valid(self, form):
        messages.success(self.request, 'Profesional creado exitosamente.')
        return super().form_valid(form)


class ProfessionalUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Editar un profesional."""

    model = Professional
    form_class = ProfessionalForm
    template_name = 'clinic/professional_form.html'
    success_url = reverse_lazy('clinic:professional_list')

    def form_valid(self, form):
        messages.success(self.request, 'Profesional actualizado exitosamente.')
        return super().form_valid(form)


class ProfessionalDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Eliminar un profesional."""

    model = Professional
    template_name = 'clinic/professional_confirm_delete.html'
    success_url = reverse_lazy('clinic:professional_list')

    def form_valid(self, form):
        messages.success(self.request, 'Profesional eliminado exitosamente.')
        return super().form_valid(form)


# Schedule Views
class ScheduleListView(LoginRequiredMixin, ListView):
    """Lista de horarios."""

    model = Schedule
    template_name = 'clinic/schedule_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        return super().get_queryset().select_related('clinic', 'professional')


class ScheduleCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Crear un horario."""

    model = Schedule
    form_class = ScheduleForm
    template_name = 'clinic/schedule_form.html'
    success_url = reverse_lazy('clinic:schedule_list')

    def form_valid(self, form):
        messages.success(self.request, 'Horario creado exitosamente.')
        return super().form_valid(form)


class ScheduleUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Editar un horario."""

    model = Schedule
    form_class = ScheduleForm
    template_name = 'clinic/schedule_form.html'
    success_url = reverse_lazy('clinic:schedule_list')

    def form_valid(self, form):
        messages.success(self.request, 'Horario actualizado exitosamente.')
        return super().form_valid(form)


class ScheduleDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Eliminar un horario."""

    model = Schedule
    template_name = 'clinic/schedule_confirm_delete.html'
    success_url = reverse_lazy('clinic:schedule_list')

    def form_valid(self, form):
        messages.success(self.request, 'Horario eliminado exitosamente.')
        return super().form_valid(form)


# Message Template Views
class MessageTemplateListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Lista de plantillas de mensajes."""

    model = MessageTemplate
    template_name = 'clinic/messagetemplate_list.html'
    context_object_name = 'templates'


class MessageTemplateCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Crear una plantilla de mensaje."""

    model = MessageTemplate
    form_class = MessageTemplateForm
    template_name = 'clinic/messagetemplate_form.html'
    success_url = reverse_lazy('clinic:messagetemplate_list')

    def form_valid(self, form):
        messages.success(self.request, 'Plantilla creada exitosamente.')
        return super().form_valid(form)


class MessageTemplateUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Editar una plantilla de mensaje."""

    model = MessageTemplate
    form_class = MessageTemplateForm
    template_name = 'clinic/messagetemplate_form.html'
    success_url = reverse_lazy('clinic:messagetemplate_list')

    def form_valid(self, form):
        messages.success(self.request, 'Plantilla actualizada exitosamente.')
        return super().form_valid(form)


class MessageTemplateDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Eliminar una plantilla de mensaje."""

    model = MessageTemplate
    template_name = 'clinic/messagetemplate_confirm_delete.html'
    success_url = reverse_lazy('clinic:messagetemplate_list')

    def form_valid(self, form):
        messages.success(self.request, 'Plantilla eliminada exitosamente.')
        return super().form_valid(form)
