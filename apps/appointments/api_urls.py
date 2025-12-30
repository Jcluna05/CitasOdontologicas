"""
API URLs para la app appointments.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    ProcedureTypeViewSet,
    AppointmentViewSet,
    AvailabilityAPIView,
    DashboardStatsAPIView,
)

router = DefaultRouter()
router.register(r'procedures', ProcedureTypeViewSet, basename='procedure')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
    path('availability/', AvailabilityAPIView.as_view(), name='api_availability'),
    path('dashboard/stats/', DashboardStatsAPIView.as_view(), name='api_dashboard_stats'),
]
