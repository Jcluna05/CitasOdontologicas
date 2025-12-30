"""
URLs para la app accounts.
"""

from django.urls import path

from .views import (
    CustomLoginView,
    CustomLogoutView,
    DashboardView,
    UserListView,
    UserCreateView,
    UserUpdateView,
    UserDeleteView,
    ProfileView,
    ProfileUpdateView,
)

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # Dashboard (sin namespace para facilitar redirect)
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Users management
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),

    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
]

# URL del dashboard sin namespace (para redirect global)
from django.urls import path as global_path
