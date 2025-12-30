"""
API URLs para la app accounts.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    LoginAPIView,
    LogoutAPIView,
    CurrentUserAPIView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('auth/me/', CurrentUserAPIView.as_view(), name='api_current_user'),
    path('', include(router.urls)),
]
