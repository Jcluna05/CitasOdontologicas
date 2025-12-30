"""
URLs para la app inventory.
"""

from django.urls import path

from .views import (
    # Dashboard
    InventoryDashboardView,
    # Categories
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView,
    CategoryDeleteView,
    # Suppliers
    SupplierListView,
    SupplierCreateView,
    SupplierUpdateView,
    SupplierDeleteView,
    # Products
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    # Stock Movements
    StockEntryView,
    StockExitView,
    StockAdjustmentView,
    MovementListView,
)

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', InventoryDashboardView.as_view(), name='dashboard'),

    # Categories
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),

    # Suppliers
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/edit/', SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier_delete'),

    # Products
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    # Stock Movements
    path('products/<int:pk>/entry/', StockEntryView.as_view(), name='stock_entry'),
    path('products/<int:pk>/exit/', StockExitView.as_view(), name='stock_exit'),
    path('products/<int:pk>/adjustment/', StockAdjustmentView.as_view(), name='stock_adjustment'),
    path('movements/', MovementListView.as_view(), name='movement_list'),
]
