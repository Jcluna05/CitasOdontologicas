"""
Formularios para la app patients.
"""

from django import forms

from .models import Patient, PatientEvent


class PatientForm(forms.ModelForm):
    """Formulario para crear/editar pacientes."""

    class Meta:
        model = Patient
        fields = [
            'medical_record_number', 'first_name', 'last_name',
            'birth_date', 'gender', 'phone', 'whatsapp', 'email', 'address',
            'has_anxiety', 'has_allergies', 'allergies_detail',
            'has_acute_pain', 'is_child', 'is_elderly',
            'medical_notes', 'observations', 'status'
        ]
        widgets = {
            'medical_record_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: HC-2024-0001'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '999-999-999'
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '999-999-999'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dirección completa'
            }),
            'has_anxiety': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_allergies': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allergies_detail': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Detalle de alergias'
            }),
            'has_acute_pain': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_child': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_elderly': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'medical_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas médicas importantes'
            }),
            'observations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones generales'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class PatientQuickForm(forms.ModelForm):
    """Formulario rápido para crear pacientes (campos mínimos)."""

    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'phone', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '999-999-999'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.medical_record_number:
            instance.medical_record_number = Patient.generate_medical_record_number()
        if commit:
            instance.save()
        return instance


class PatientTriageForm(forms.ModelForm):
    """Formulario de triage rápido."""

    class Meta:
        model = Patient
        fields = [
            'has_anxiety', 'has_allergies', 'allergies_detail',
            'has_acute_pain', 'is_child', 'is_elderly'
        ]
        widgets = {
            'has_anxiety': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_allergies': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allergies_detail': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'has_acute_pain': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_child': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_elderly': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PatientEventForm(forms.ModelForm):
    """Formulario para eventos del paciente."""

    class Meta:
        model = PatientEvent
        fields = ['event_type', 'description']
        widgets = {
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


class PatientSearchForm(forms.Form):
    """Formulario de búsqueda de pacientes."""

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, teléfono o historia clínica...'
        })
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + list(Patient.Status.choices),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
