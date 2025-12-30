"""
Serializadores para la API de inventario.
"""

from decimal import Decimal
from rest_framework import serializers
from .models import Category, Supplier, Product, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    """Serializador para categorías."""

    product_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'color', 'icon',
            'is_active', 'order', 'product_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SupplierSerializer(serializers.ModelSerializer):
    """Serializador para proveedores."""

    product_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_name', 'phone', 'email',
            'address', 'notes', 'is_active', 'product_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Serializador simplificado para lista de productos."""

    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    stock_status = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'code', 'name', 'brand',
            'category', 'category_name',
            'supplier', 'supplier_name',
            'current_stock', 'minimum_stock', 'unit_display',
            'purchase_price', 'stock_status', 'is_active'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializador completo para detalle de producto."""

    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    stock_percentage = serializers.FloatField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'code', 'name', 'description', 'brand',
            'category', 'category_name',
            'supplier', 'supplier_name',
            'unit', 'unit_display',
            'current_stock', 'minimum_stock', 'maximum_stock',
            'purchase_price', 'sale_price',
            'expiration_date', 'location',
            'is_active', 'stock_status', 'stock_percentage',
            'is_low_stock', 'is_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['current_stock', 'created_at', 'updated_at']


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializador para crear/actualizar productos."""

    class Meta:
        model = Product
        fields = [
            'code', 'name', 'description', 'brand',
            'category', 'supplier', 'unit',
            'minimum_stock', 'maximum_stock',
            'purchase_price', 'sale_price',
            'expiration_date', 'location', 'is_active'
        ]


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializador para movimientos de stock."""

    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_short_name', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'product_code',
            'movement_type', 'movement_type_display',
            'quantity', 'previous_stock', 'new_stock',
            'unit_cost', 'notes',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['previous_stock', 'new_stock', 'created_by', 'created_at']


class StockEntrySerializer(serializers.Serializer):
    """Serializador para entrada de stock."""

    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0'), required=False)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)


class StockExitSerializer(serializers.Serializer):
    """Serializador para salida de stock."""

    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    reason = serializers.ChoiceField(choices=[
        ('use', 'Uso en procedimiento'),
        ('damaged', 'Dañado'),
        ('expired', 'Vencido'),
        ('lost', 'Pérdida'),
        ('other', 'Otro'),
    ])
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)


class StockAdjustmentSerializer(serializers.Serializer):
    """Serializador para ajuste de inventario."""

    new_quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0'))
    notes = serializers.CharField(max_length=500)


class InventoryDashboardSerializer(serializers.Serializer):
    """Serializador para dashboard de inventario."""

    total_products = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    out_of_stock_count = serializers.IntegerField()
    expiring_soon = serializers.IntegerField()
    expired_count = serializers.IntegerField()
    inventory_value = serializers.DecimalField(max_digits=12, decimal_places=2)
