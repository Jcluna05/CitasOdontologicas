"""
API URLs para la app clinic.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    ClinicViewSet,
    ProfessionalViewSet,
    ScheduleViewSet,
    MessageTemplateViewSet,
)

router = DefaultRouter()
router.register(r'clinics', ClinicViewSet, basename='clinic')
router.register(r'professionals', ProfessionalViewSet, basename='professional')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'message-templates', MessageTemplateViewSet, basename='messagetemplate')

urlpatterns = [
    path('', include(router.urls)),
]
