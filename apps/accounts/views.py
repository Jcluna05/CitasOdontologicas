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

from apps.appointments.models import Appointment
from apps.patients.models import Patient

from .forms import CustomAuthenticationForm, CustomUserCreationForm, CustomUserChangeForm, ProfileForm
from .models import User


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
    """Dashboard principal del sistema."""

    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Citas de hoy
        appointments_today = Appointment.objects.filter(date=today)
        if self.request.user.is_professional:
            appointments_today = appointments_today.filter(
                professional__user=self.request.user
            )

        context['appointments_today'] = appointments_today.order_by('start_time')[:10]
        context['appointments_today_count'] = appointments_today.count()

        # Estadísticas rápidas
        context['patients_count'] = Patient.objects.count()
        context['pending_count'] = Appointment.objects.filter(
            date=today,
            status=Appointment.Status.PENDING
        ).count()
        context['confirmed_count'] = Appointment.objects.filter(
            date=today,
            status=Appointment.Status.CONFIRMED
        ).count()

        # Próximas citas (próximos 7 días)
        from datetime import timedelta
        week_later = today + timedelta(days=7)
        context['upcoming_appointments'] = Appointment.objects.filter(
            date__gt=today,
            date__lte=week_later,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).order_by('date', 'start_time')[:5]

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
