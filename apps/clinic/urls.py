"""
URLs para la app clinic.
"""

from django.urls import path

from .views import (
    ClinicSettingsView,
    ProfessionalListView,
    ProfessionalDetailView,
    ProfessionalCreateView,
    ProfessionalUpdateView,
    ProfessionalDeleteView,
    ScheduleListView,
    ScheduleCreateView,
    ScheduleUpdateView,
    ScheduleDeleteView,
    MessageTemplateListView,
    MessageTemplateCreateView,
    MessageTemplateUpdateView,
    MessageTemplateDeleteView,
)

app_name = 'clinic'

urlpatterns = [
    # Clinic settings
    path('settings/', ClinicSettingsView.as_view(), name='settings'),

    # Professionals
    path('professionals/', ProfessionalListView.as_view(), name='professional_list'),
    path('professionals/create/', ProfessionalCreateView.as_view(), name='professional_create'),
    path('professionals/<int:pk>/', ProfessionalDetailView.as_view(), name='professional_detail'),
    path('professionals/<int:pk>/edit/', ProfessionalUpdateView.as_view(), name='professional_edit'),
    path('professionals/<int:pk>/delete/', ProfessionalDeleteView.as_view(), name='professional_delete'),

    # Schedules
    path('schedules/', ScheduleListView.as_view(), name='schedule_list'),
    path('schedules/create/', ScheduleCreateView.as_view(), name='schedule_create'),
    path('schedules/<int:pk>/edit/', ScheduleUpdateView.as_view(), name='schedule_edit'),
    path('schedules/<int:pk>/delete/', ScheduleDeleteView.as_view(), name='schedule_delete'),

    # Message Templates
    path('templates/', MessageTemplateListView.as_view(), name='messagetemplate_list'),
    path('templates/create/', MessageTemplateCreateView.as_view(), name='messagetemplate_create'),
    path('templates/<int:pk>/edit/', MessageTemplateUpdateView.as_view(), name='messagetemplate_edit'),
    path('templates/<int:pk>/delete/', MessageTemplateDeleteView.as_view(), name='messagetemplate_delete'),
]
