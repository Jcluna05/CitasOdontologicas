"""
URLs para la app appointments.
"""

from django.urls import path

from .views import (
    # Appointments
    AppointmentListView,
    AppointmentDayView,
    AppointmentDetailView,
    AppointmentCreateView,
    AppointmentUpdateView,
    AppointmentDeleteView,
    AppointmentConfirmView,
    AppointmentCancelView,
    AppointmentAttendedView,
    AppointmentNoShowView,
    AppointmentRescheduleView,
    AppointmentCopyMessageView,
    # Procedure Types
    ProcedureTypeListView,
    ProcedureTypeCreateView,
    ProcedureTypeUpdateView,
    ProcedureTypeDeleteView,
    # Availability
    AvailabilityView,
)

app_name = 'appointments'

urlpatterns = [
    # Appointments
    path('', AppointmentListView.as_view(), name='appointment_list'),
    path('day/', AppointmentDayView.as_view(), name='appointment_day'),
    path('create/', AppointmentCreateView.as_view(), name='appointment_create'),
    path('<int:pk>/', AppointmentDetailView.as_view(), name='appointment_detail'),
    path('<int:pk>/edit/', AppointmentUpdateView.as_view(), name='appointment_edit'),
    path('<int:pk>/delete/', AppointmentDeleteView.as_view(), name='appointment_delete'),

    # Status changes
    path('<int:pk>/confirm/', AppointmentConfirmView.as_view(), name='appointment_confirm'),
    path('<int:pk>/cancel/', AppointmentCancelView.as_view(), name='appointment_cancel'),
    path('<int:pk>/attended/', AppointmentAttendedView.as_view(), name='appointment_attended'),
    path('<int:pk>/no-show/', AppointmentNoShowView.as_view(), name='appointment_no_show'),
    path('<int:pk>/reschedule/', AppointmentRescheduleView.as_view(), name='appointment_reschedule'),

    # Message
    path('<int:pk>/message/', AppointmentCopyMessageView.as_view(), name='appointment_message'),

    # Procedure Types
    path('procedures/', ProcedureTypeListView.as_view(), name='proceduretype_list'),
    path('procedures/create/', ProcedureTypeCreateView.as_view(), name='proceduretype_create'),
    path('procedures/<int:pk>/edit/', ProcedureTypeUpdateView.as_view(), name='proceduretype_edit'),
    path('procedures/<int:pk>/delete/', ProcedureTypeDeleteView.as_view(), name='proceduretype_delete'),

    # Availability
    path('availability/', AvailabilityView.as_view(), name='availability'),
]
