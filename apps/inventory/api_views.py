"""
API views para la app inventory.
"""

from datetime import timedelta

from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Category, Supplier, Product, StockMovement
from .serializers import (
    CategorySerializer,
    SupplierSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    StockMovementSerializer,
    StockEntrySerializer,
    StockExitSerializer,
    StockAdjustmentSerializer,
    InventoryDashboardSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para categorías de inventario."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order', 'created_at']
    ordering = ['order', 'name']

    def get_queryset(self):
        return Category.objects.annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        )


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet para proveedores."""

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'contact_name', 'email', 'phone']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        return Supplier.objects.annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        )


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet para productos."""

    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'supplier', 'is_active']
    search_fields = ['name', 'code', 'brand', 'description']
    ordering_fields = ['name', 'code', 'current_stock', 'purchase_price', 'created_at']
    ordering = ['category', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'supplier')

        # Filtro por estado de stock
        stock_status = self.request.query_params.get('stock_status')
        if stock_status == 'low':
            queryset = queryset.filter(
                current_stock__lte=F('minimum_stock'),
                current_stock__gt=0
            )
        elif stock_status == 'out':
            queryset = queryset.filter(current_stock__lte=0)
        elif stock_status == 'ok':
            queryset = queryset.filter(current_stock__gt=F('minimum_stock'))
        elif stock_status == 'expiring':
            today = timezone.now().date()
            queryset = queryset.filter(
                expiration_date__isnull=False,
                expiration_date__lte=today + timedelta(days=30)
            )

        return queryset

    @action(detail=True, methods=['post'])
    def entry(self, request, pk=None):
        """Registrar entrada de stock."""
        product = self.get_object()
        serializer = StockEntrySerializer(data=request.data)

        if serializer.is_valid():
            try:
                product.add_stock(
                    quantity=serializer.validated_data['quantity'],
                    user=request.user,
                    notes=serializer.validated_data.get('notes', ''),
                    cost=serializer.validated_data.get('unit_cost'),
                )
                return Response({
                    'message': 'Entrada registrada exitosamente',
                    'current_stock': product.current_stock
                })
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def exit(self, request, pk=None):
        """Registrar salida de stock."""
        product = self.get_object()
        serializer = StockExitSerializer(data=request.data)

        if serializer.is_valid():
            try:
                product.remove_stock(
                    quantity=serializer.validated_data['quantity'],
                    user=request.user,
                    notes=serializer.validated_data.get('notes', ''),
                    reason=serializer.validated_data['reason'],
                )
                return Response({
                    'message': 'Salida registrada exitosamente',
                    'current_stock': product.current_stock
                })
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def adjustment(self, request, pk=None):
        """Registrar ajuste de inventario."""
        product = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)

        if serializer.is_valid():
            try:
                product.adjust_stock(
                    new_quantity=serializer.validated_data['new_quantity'],
                    user=request.user,
                    notes=serializer.validated_data['notes'],
                )
                return Response({
                    'message': 'Ajuste registrado exitosamente',
                    'current_stock': product.current_stock
                })
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Obtener historial de movimientos del producto."""
        product = self.get_object()
        movements = product.movements.select_related('created_by').order_by('-created_at')[:50]
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para movimientos de stock."""

    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['product', 'movement_type', 'created_by']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return StockMovement.objects.select_related(
            'product', 'product__category', 'created_by'
        )


class InventoryDashboardViewSet(viewsets.ViewSet):
    """ViewSet para dashboard de inventario."""

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Obtener estadísticas del dashboard."""
        products = Product.objects.filter(is_active=True)
        today = timezone.now().date()

        data = {
            'total_products': products.count(),
            'low_stock_count': products.filter(
                current_stock__lte=F('minimum_stock'),
                current_stock__gt=0
            ).count(),
            'out_of_stock_count': products.filter(current_stock__lte=0).count(),
            'expiring_soon': products.filter(
                expiration_date__isnull=False,
                expiration_date__lte=today + timedelta(days=30),
                expiration_date__gt=today
            ).count(),
            'expired_count': products.filter(
                expiration_date__isnull=False,
                expiration_date__lt=today
            ).count(),
            'inventory_value': products.aggregate(
                total=Sum(F('current_stock') * F('purchase_price'))
            )['total'] or 0,
        }

        serializer = InventoryDashboardSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Obtener productos con stock bajo."""
        products = Product.objects.filter(
            is_active=True,
            current_stock__lte=F('minimum_stock'),
            current_stock__gt=0
        ).select_related('category')[:20]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expiring(self, request):
        """Obtener productos por vencer."""
        today = timezone.now().date()
        products = Product.objects.filter(
            is_active=True,
            expiration_date__isnull=False,
            expiration_date__lte=today + timedelta(days=30),
            expiration_date__gt=today
        ).select_related('category').order_by('expiration_date')[:20]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Obtener productos sin stock."""
        products = Product.objects.filter(
            is_active=True,
            current_stock__lte=0
        ).select_related('category')[:20]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
