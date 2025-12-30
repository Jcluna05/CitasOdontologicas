"""
Vistas para la app inventory.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q, F
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView
)

from .models import Category, Supplier, Product, StockMovement
from .forms import (
    CategoryForm, SupplierForm, ProductForm,
    StockEntryForm, StockExitForm, StockAdjustmentForm
)


# =============================================================================
# Dashboard de Inventario
# =============================================================================

class InventoryDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal de inventario."""

    template_name = 'inventory/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas generales
        products = Product.objects.filter(is_active=True)
        context['total_products'] = products.count()
        context['low_stock_count'] = products.filter(
            current_stock__lte=F('minimum_stock')
        ).count()
        context['out_of_stock_count'] = products.filter(current_stock__lte=0).count()

        # Productos vencidos o por vencer
        today = timezone.now().date()
        from datetime import timedelta
        context['expiring_soon'] = products.filter(
            expiration_date__isnull=False,
            expiration_date__lte=today + timedelta(days=30),
            expiration_date__gt=today
        ).count()
        context['expired_count'] = products.filter(
            expiration_date__isnull=False,
            expiration_date__lt=today
        ).count()

        # Valor total del inventario
        context['inventory_value'] = products.aggregate(
            total=Sum(F('current_stock') * F('purchase_price'))
        )['total'] or 0

        # Productos con stock bajo
        context['low_stock_products'] = products.filter(
            current_stock__lte=F('minimum_stock'),
            current_stock__gt=0
        ).select_related('category')[:10]

        # Productos sin stock
        context['out_of_stock_products'] = products.filter(
            current_stock__lte=0
        ).select_related('category')[:5]

        # Productos por vencer
        context['expiring_products'] = products.filter(
            expiration_date__isnull=False,
            expiration_date__lte=today + timedelta(days=30),
            expiration_date__gt=today
        ).select_related('category').order_by('expiration_date')[:5]

        # Últimos movimientos
        context['recent_movements'] = StockMovement.objects.select_related(
            'product', 'created_by'
        ).order_by('-created_at')[:10]

        # Categorías con conteo
        context['categories'] = Category.objects.filter(is_active=True).annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        )

        return context


# =============================================================================
# Categorías
# =============================================================================

class CategoryListView(LoginRequiredMixin, ListView):
    """Lista de categorías."""

    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.annotate(
            product_count=Count('products', filter=Q(products__is_active=True)),
            low_stock=Count('products', filter=Q(
                products__is_active=True,
                products__current_stock__lte=F('products__minimum_stock')
            ))
        ).order_by('order', 'name')


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Crear categoría."""

    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría creada exitosamente.')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """Editar categoría."""

    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('inventory:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada exitosamente.')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar categoría."""

    model = Category
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('inventory:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Categoría eliminada exitosamente.')
        return super().form_valid(form)


# =============================================================================
# Proveedores
# =============================================================================

class SupplierListView(LoginRequiredMixin, ListView):
    """Lista de proveedores."""

    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

    def get_queryset(self):
        return Supplier.objects.annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).order_by('name')


class SupplierCreateView(LoginRequiredMixin, CreateView):
    """Crear proveedor."""

    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor creado exitosamente.')
        return super().form_valid(form)


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    """Editar proveedor."""

    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor actualizado exitosamente.')
        return super().form_valid(form)


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar proveedor."""

    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor eliminado exitosamente.')
        return super().form_valid(form)


# =============================================================================
# Productos
# =============================================================================

class ProductListView(LoginRequiredMixin, ListView):
    """Lista de productos."""

    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'supplier')

        # Filtros
        category = self.request.GET.get('category')
        status = self.request.GET.get('status')
        search = self.request.GET.get('q')

        if category:
            queryset = queryset.filter(category_id=category)

        if status == 'low':
            queryset = queryset.filter(
                current_stock__lte=F('minimum_stock'),
                current_stock__gt=0
            )
        elif status == 'out':
            queryset = queryset.filter(current_stock__lte=0)
        elif status == 'ok':
            queryset = queryset.filter(current_stock__gt=F('minimum_stock'))
        elif status == 'expiring':
            from datetime import timedelta
            today = timezone.now().date()
            queryset = queryset.filter(
                expiration_date__isnull=False,
                expiration_date__lte=today + timedelta(days=30)
            )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(brand__icontains=search)
            )

        return queryset.order_by('category', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    """Detalle de producto."""

    model = Product
    template_name = 'inventory/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movements'] = self.object.movements.select_related(
            'created_by'
        ).order_by('-created_at')[:20]
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Crear producto."""

    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:product_list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto creado exitosamente.')
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Editar producto."""

    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'

    def get_success_url(self):
        return reverse_lazy('inventory:product_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado exitosamente.')
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar producto."""

    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:product_list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto eliminado exitosamente.')
        return super().form_valid(form)


# =============================================================================
# Movimientos de Stock
# =============================================================================

class StockEntryView(LoginRequiredMixin, FormView):
    """Entrada de stock."""

    template_name = 'inventory/stock_entry.html'
    form_class = StockEntryForm

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def form_valid(self, form):
        try:
            self.product.add_stock(
                quantity=form.cleaned_data['quantity'],
                user=self.request.user,
                notes=form.cleaned_data.get('notes', ''),
                cost=form.cleaned_data.get('unit_cost'),
            )
            messages.success(
                self.request,
                f'Entrada registrada: +{form.cleaned_data["quantity"]} {self.product.get_unit_display()}'
            )
        except ValueError as e:
            messages.error(self.request, str(e))

        return redirect('inventory:product_detail', pk=self.product.pk)


class StockExitView(LoginRequiredMixin, FormView):
    """Salida de stock."""

    template_name = 'inventory/stock_exit.html'
    form_class = StockExitForm

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product'] = self.product
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def form_valid(self, form):
        try:
            self.product.remove_stock(
                quantity=form.cleaned_data['quantity'],
                user=self.request.user,
                notes=form.cleaned_data.get('notes', ''),
                reason=form.cleaned_data['reason'],
            )
            messages.success(
                self.request,
                f'Salida registrada: -{form.cleaned_data["quantity"]} {self.product.get_unit_display()}'
            )
        except ValueError as e:
            messages.error(self.request, str(e))

        return redirect('inventory:product_detail', pk=self.product.pk)


class StockAdjustmentView(LoginRequiredMixin, FormView):
    """Ajuste de inventario."""

    template_name = 'inventory/stock_adjustment.html'
    form_class = StockAdjustmentForm

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def form_valid(self, form):
        try:
            self.product.adjust_stock(
                new_quantity=form.cleaned_data['new_quantity'],
                user=self.request.user,
                notes=form.cleaned_data['notes'],
            )
            messages.success(self.request, 'Ajuste de inventario registrado.')
        except ValueError as e:
            messages.error(self.request, str(e))

        return redirect('inventory:product_detail', pk=self.product.pk)


class MovementListView(LoginRequiredMixin, ListView):
    """Historial de movimientos."""

    model = StockMovement
    template_name = 'inventory/movement_list.html'
    context_object_name = 'movements'
    paginate_by = 30

    def get_queryset(self):
        queryset = StockMovement.objects.select_related(
            'product', 'product__category', 'created_by'
        )

        # Filtros
        product = self.request.GET.get('product')
        movement_type = self.request.GET.get('type')

        if product:
            queryset = queryset.filter(product_id=product)
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movement_types'] = StockMovement.MovementType.choices
        context['selected_type'] = self.request.GET.get('type', '')
        return context
