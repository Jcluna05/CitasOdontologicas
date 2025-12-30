"""
Configuración del admin para la app inventory.
"""

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import Category, Supplier, Product, StockMovement


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """Admin para categorías de inventario."""

    list_display = ('name', 'color_display', 'products_count', 'low_stock_count', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_active')
    ordering = ('order', 'name')

    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 15px; '
            'border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Color'


@admin.register(Supplier)
class SupplierAdmin(ModelAdmin):
    """Admin para proveedores."""

    list_display = ('name', 'contact_name', 'phone', 'email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_name', 'email')


class StockMovementInline(TabularInline):
    """Inline para movimientos de stock."""

    model = StockMovement
    extra = 0
    readonly_fields = ('movement_type', 'quantity', 'unit_cost', 'created_by', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    """Admin para productos."""

    list_display = (
        'code', 'name', 'category', 'brand',
        'current_stock', 'unit', 'stock_status_badge', 'is_active'
    )
    list_filter = ('category', 'supplier', 'is_active', 'unit')
    search_fields = ('code', 'name', 'brand', 'description')
    readonly_fields = ('current_stock', 'created_at', 'updated_at')
    inlines = [StockMovementInline]

    fieldsets = (
        ('Identificación', {
            'fields': ('code', 'name', 'description', 'brand')
        }),
        ('Clasificación', {
            'fields': ('category', 'supplier', 'clinic')
        }),
        ('Stock', {
            'fields': ('unit', 'current_stock', 'minimum_stock', 'maximum_stock')
        }),
        ('Precios', {
            'fields': ('purchase_price', 'sale_price')
        }),
        ('Control', {
            'fields': ('expiration_date', 'location', 'is_active')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def stock_status_badge(self, obj):
        status = obj.stock_status
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            status['color'],
            status['label']
        )
    stock_status_badge.short_description = 'Estado'


@admin.register(StockMovement)
class StockMovementAdmin(ModelAdmin):
    """Admin para movimientos de stock."""

    list_display = (
        'created_at', 'product', 'movement_type',
        'quantity_display', 'unit_cost', 'created_by'
    )
    list_filter = ('movement_type', 'created_at', 'product__category')
    search_fields = ('product__name', 'product__code', 'notes')
    readonly_fields = ('product', 'movement_type', 'quantity', 'unit_cost', 'created_by', 'created_at')
    date_hierarchy = 'created_at'

    def quantity_display(self, obj):
        sign = '+' if obj.is_entry else '-'
        color = 'success' if obj.is_entry else 'danger'
        return format_html(
            '<span style="color: var(--color-{});">{}{}</span>',
            color,
            sign,
            obj.quantity
        )
    quantity_display.short_description = 'Cantidad'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
