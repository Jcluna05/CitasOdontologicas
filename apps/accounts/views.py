"""
Vistas para la app accounts.
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from apps.appointments.models import Appointment, ProcedureType
from apps.patients.models import Patient
from apps.clinic.models import Clinic

from .forms import CustomAuthenticationForm, CustomUserCreationForm, CustomUserChangeForm, ProfileForm
from .models import User
from .services import DashboardService


class CustomLoginView(LoginView):
    """Vista de login personalizada."""

    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard')


class CustomLogoutView(LogoutView):
    """Vista de logout personalizada."""

    next_page = 'accounts:login'


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal del sistema - Centro de operaciones clínicas."""

    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Inicializar servicio
        service = DashboardService(self.request.user)

        # Datos del header
        context['today'] = timezone.now()
        context['clinic'] = Clinic.get_default()

        # KPIs del día
        context['stats'] = service.get_today_stats()

        # Agenda de hoy
        context['appointments_today'] = service.get_today_appointments(limit=10)

        # Alertas inteligentes
        context['alerts'] = service.get_smart_alerts()

        # Slots disponibles
        context['available_slots'] = service.get_available_slots(limit=5)

        # Estadísticas semanales
        context['weekly_stats'] = service.get_weekly_stats()

        # Huecos en la agenda
        context['schedule_gaps'] = service.get_gaps_in_schedule(min_gap_minutes=45)

        # Próximas citas
        context['upcoming_appointments'] = service.get_upcoming_appointments(days=7, limit=5)

        # Tipos de procedimiento para el widget de disponibilidad
        context['procedure_types'] = ProcedureType.objects.filter(is_active=True).order_by('order')

        return context


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin que requiere que el usuario sea administrador."""

    def test_func(self):
        return self.request.user.is_admin


class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Lista de usuarios."""

    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20


class UserCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Crear nuevo usuario."""

    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado exitosamente.')
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Editar usuario."""

    model = User
    form_class = CustomUserChangeForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado exitosamente.')
        return super().form_valid(form)


class UserDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Eliminar usuario."""

    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Usuario eliminado exitosamente.')
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    """Ver perfil del usuario actual."""

    template_name = 'accounts/profile.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Editar perfil del usuario actual."""

    model = User
    form_class = ProfileForm
    template_name = 'accounts/profile_form.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado exitosamente.')
        return super().form_valid(form)
