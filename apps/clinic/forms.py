"""
Formularios para la app clinic.
"""

from django import forms
from django.forms import inlineformset_factory

from .models import Clinic, Professional, Schedule, MessageTemplate


class ClinicForm(forms.ModelForm):
    """Formulario para el consultorio."""

    class Meta:
        model = Clinic
        fields = [
            'name', 'phone', 'whatsapp', 'email', 'address',
            'logo', 'appointment_duration_default', 'allow_online_booking'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'appointment_duration_default': forms.NumberInput(attrs={'class': 'form-control'}),
            'allow_online_booking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProfessionalForm(forms.ModelForm):
    """Formulario para profesionales."""

    class Meta:
        model = Professional
        fields = ['user', 'clinic', 'specialty', 'license_number', 'color', 'is_active']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'clinic': forms.Select(attrs={'class': 'form-select'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ScheduleForm(forms.ModelForm):
    """Formulario para horarios."""

    class Meta:
        model = Schedule
        fields = ['clinic', 'professional', 'weekday', 'start_time', 'end_time', 'is_active']
        widgets = {
            'clinic': forms.Select(attrs={'class': 'form-select'}),
            'professional': forms.Select(attrs={'class': 'form-select'}),
            'weekday': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# Formset para horarios
ScheduleFormSet = inlineformset_factory(
    Clinic,
    Schedule,
    form=ScheduleForm,
    extra=7,  # One for each day
    can_delete=True,
    fields=['weekday', 'start_time', 'end_time', 'is_active']
)


class MessageTemplateForm(forms.ModelForm):
    """Formulario para plantillas de mensajes."""

    class Meta:
        model = MessageTemplate
        fields = ['clinic', 'template_type', 'subject', 'message', 'is_active']
        widgets = {
            'clinic': forms.Select(attrs={'class': 'form-select'}),
            'template_type': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
