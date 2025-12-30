"""
Formularios para la app appointments.
"""

from django import forms
from django.utils import timezone

from apps.clinic.models import Professional
from apps.patients.models import Patient

from .models import Appointment, ProcedureType


class AppointmentForm(forms.ModelForm):
    """Formulario para crear/editar citas."""

    class Meta:
        model = Appointment
        fields = [
            'patient', 'professional', 'procedure_type',
            'date', 'start_time', 'end_time', 'notes'
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'professional': forms.Select(attrs={'class': 'form-select'}),
            'procedure_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.filter(
            status='active'
        ).order_by('last_name', 'first_name')
        self.fields['professional'].queryset = Professional.objects.filter(
            is_active=True
        ).select_related('user')
        self.fields['procedure_type'].queryset = ProcedureType.objects.filter(
            is_active=True
        ).order_by('order', 'name')
        self.fields['end_time'].required = False

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        procedure_type = cleaned_data.get('procedure_type')
        end_time = cleaned_data.get('end_time')

        # Auto-calcular end_time si no se proporciona
        if start_time and procedure_type and not end_time:
            from datetime import datetime, timedelta, date
            start_datetime = datetime.combine(date.today(), start_time)
            end_datetime = start_datetime + timedelta(minutes=procedure_type.duration_minutes)
            cleaned_data['end_time'] = end_datetime.time()

        return cleaned_data


class AppointmentQuickForm(forms.ModelForm):
    """Formulario rápido para crear citas."""

    patient_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar paciente...',
            'autocomplete': 'off',
        })
    )

    class Meta:
        model = Appointment
        fields = ['patient', 'professional', 'procedure_type', 'date', 'start_time', 'notes']
        widgets = {
            'patient': forms.HiddenInput(),
            'professional': forms.Select(attrs={'class': 'form-select'}),
            'procedure_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notas...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['professional'].queryset = Professional.objects.filter(
            is_active=True
        ).select_related('user')
        self.fields['procedure_type'].queryset = ProcedureType.objects.filter(
            is_active=True
        ).order_by('order', 'name')


class AppointmentStatusForm(forms.Form):
    """Formulario para cambiar el estado de una cita."""

    status = forms.ChoiceField(
        choices=Appointment.Status.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Notas del cambio de estado...'
        })
    )


class AppointmentCancelForm(forms.Form):
    """Formulario para cancelar una cita."""

    cancellation_reason = forms.CharField(
        label='Motivo de cancelación',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Indique el motivo de la cancelación...'
        })
    )


class AppointmentRescheduleForm(forms.Form):
    """Formulario para reprogramar una cita."""

    new_date = forms.DateField(
        label='Nueva fecha',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    new_start_time = forms.TimeField(
        label='Nueva hora',
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    reason = forms.CharField(
        label='Motivo de reprogramación',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2
        })
    )


class ProcedureTypeForm(forms.ModelForm):
    """Formulario para tipos de procedimientos."""

    class Meta:
        model = ProcedureType
        fields = [
            'name', 'description', 'duration_minutes',
            'color', 'requires_confirmation', 'is_active', 'order'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'requires_confirmation': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AppointmentFilterForm(forms.Form):
    """Formulario de filtros para la agenda."""

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    professional = forms.ModelChoiceField(
        required=False,
        queryset=Professional.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Todos los profesionales'
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos los estados')] + list(Appointment.Status.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    procedure_type = forms.ModelChoiceField(
        required=False,
        queryset=ProcedureType.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Todos los procedimientos'
    )
