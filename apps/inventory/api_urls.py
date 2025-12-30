"""
API URLs para la app inventory.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import (
    CategoryViewSet,
    SupplierViewSet,
    ProductViewSet,
    StockMovementViewSet,
    InventoryDashboardViewSet,
)

router = DefaultRouter()
router.register(r'inventory/categories', CategoryViewSet, basename='inventory-category')
router.register(r'inventory/suppliers', SupplierViewSet, basename='inventory-supplier')
router.register(r'inventory/products', ProductViewSet, basename='inventory-product')
router.register(r'inventory/movements', StockMovementViewSet, basename='inventory-movement')
router.register(r'inventory/dashboard', InventoryDashboardViewSet, basename='inventory-dashboard')

urlpatterns = router.urls
