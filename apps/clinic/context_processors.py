"""
Context processors para la app clinic.
"""

from .models import Clinic


def clinic_context(request):
    """Agregar información del consultorio al contexto global."""
    try:
        clinic = Clinic.get_default()
    except Exception:
        clinic = None

    return {
        'clinic': clinic,
    }
