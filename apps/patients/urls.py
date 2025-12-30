"""
URLs para la app patients.
"""

from django.urls import path

from .views import (
    PatientListView,
    PatientDetailView,
    PatientCreateView,
    PatientUpdateView,
    PatientDeleteView,
    PatientTriageUpdateView,
    PatientEventCreateView,
    PatientSearchAPIView,
    PatientQuickCreateView,
)

app_name = 'patients'

urlpatterns = [
    # CRUD
    path('', PatientListView.as_view(), name='patient_list'),
    path('create/', PatientCreateView.as_view(), name='patient_create'),
    path('quick-create/', PatientQuickCreateView.as_view(), name='patient_quick_create'),
    path('<int:pk>/', PatientDetailView.as_view(), name='patient_detail'),
    path('<int:pk>/edit/', PatientUpdateView.as_view(), name='patient_edit'),
    path('<int:pk>/delete/', PatientDeleteView.as_view(), name='patient_delete'),

    # Triage
    path('<int:pk>/triage/', PatientTriageUpdateView.as_view(), name='patient_triage'),

    # Events
    path('<int:pk>/events/create/', PatientEventCreateView.as_view(), name='patient_event_create'),

    # Search API
    path('search/', PatientSearchAPIView.as_view(), name='patient_search'),
]
