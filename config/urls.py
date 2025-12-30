"""
URL configuration for CitasOdontologicas project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Main app routes
    path('', include('apps.accounts.urls')),
    path('clinic/', include('apps.clinic.urls')),
    path('patients/', include('apps.patients.urls')),
    path('appointments/', include('apps.appointments.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('inventory/', include('apps.inventory.urls')),

    # API routes
    path('api/', include('apps.accounts.api_urls')),
    path('api/', include('apps.clinic.api_urls')),
    path('api/', include('apps.patients.api_urls')),
    path('api/', include('apps.appointments.api_urls')),
    path('api/', include('apps.inventory.api_urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Root redirect
    path('', RedirectView.as_view(pattern_name='accounts:dashboard', permanent=False)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Admin site customization
admin.site.site_header = 'Citas Odontológicas'
admin.site.site_title = 'Admin - Citas Odontológicas'
admin.site.index_title = 'Panel de Administración'
