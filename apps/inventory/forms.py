"""
Formularios para la app inventory.
"""

from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError

from .models import Category, Supplier, Product, StockMovement


class CategoryForm(forms.ModelForm):
    """Formulario para categorías."""

    class Meta:
        model = Category
        fields = ['name', 'description', 'color', 'icon', 'is_active', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'box-seam'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SupplierForm(forms.ModelForm):
    """Formulario para proveedores."""

    class Meta:
        model = Supplier
        fields = ['name', 'contact_name', 'phone', 'email', 'address', 'notes', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductForm(forms.ModelForm):
    """Formulario para productos."""

    class Meta:
        model = Product
        fields = [
            'code', 'name', 'description', 'brand',
            'category', 'supplier', 'unit',
            'minimum_stock', 'maximum_stock',
            'purchase_price', 'sale_price',
            'expiration_date', 'location', 'is_active'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: RES-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'maximum_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Estante A'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StockEntryForm(forms.Form):
    """Formulario para entrada de stock."""

    quantity = forms.DecimalField(
        label='Cantidad',
        min_value=Decimal('0.01'),
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'})
    )
    unit_cost = forms.DecimalField(
        label='Costo unitario',
        min_value=Decimal('0'),
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )
    notes = forms.CharField(
        label='Notas',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: Compra a proveedor X'})
    )


class StockExitForm(forms.Form):
    """Formulario para salida de stock."""

    quantity = forms.DecimalField(
        label='Cantidad',
        min_value=Decimal('0.01'),
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'})
    )
    reason = forms.ChoiceField(
        label='Motivo',
        choices=[
            ('use', 'Uso en procedimiento'),
            ('damaged', 'Dañado'),
            ('expired', 'Vencido'),
            ('lost', 'Pérdida'),
            ('other', 'Otro'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    notes = forms.CharField(
        label='Notas',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )

    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if self.product and quantity > self.product.current_stock:
            raise ValidationError(
                f'Stock insuficiente. Disponible: {self.product.current_stock}'
            )
        return quantity


class StockAdjustmentForm(forms.Form):
    """Formulario para ajuste de inventario."""

    new_quantity = forms.DecimalField(
        label='Nueva cantidad',
        min_value=Decimal('0'),
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )
    notes = forms.CharField(
        label='Motivo del ajuste',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: Inventario físico'})
    )
