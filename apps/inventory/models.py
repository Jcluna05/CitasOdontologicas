"""
Modelos para la gestión de inventario odontológico.
"""

from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.clinic.models import Clinic


class Category(models.Model):
    """
    Categorías de productos de inventario.
    Ej: Resinas, Anestésicos, Instrumental, Desechables, etc.
    """

    name = models.CharField(_('nombre'), max_length=100)
    description = models.TextField(_('descripción'), blank=True)
    color = models.CharField(
        _('color'),
        max_length=7,
        default='#6B7280',
        help_text=_('Color para identificación visual')
    )
    icon = models.CharField(
        _('icono'),
        max_length=50,
        default='box-seam',
        help_text=_('Nombre del icono Bootstrap Icons')
    )
    is_active = models.BooleanField(_('activo'), default=True)
    order = models.PositiveIntegerField(_('orden'), default=0)

    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)

    class Meta:
        verbose_name = _('categoría')
        verbose_name_plural = _('categorías')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @property
    def products_count(self):
        return self.products.filter(is_active=True).count()

    @property
    def low_stock_count(self):
        return self.products.filter(
            is_active=True,
            current_stock__lte=models.F('minimum_stock')
        ).count()


class Supplier(models.Model):
    """
    Proveedores de productos odontológicos.
    """

    name = models.CharField(_('nombre'), max_length=200)
    contact_name = models.CharField(_('contacto'), max_length=100, blank=True)
    phone = models.CharField(_('teléfono'), max_length=20, blank=True)
    email = models.EmailField(_('correo electrónico'), blank=True)
    address = models.TextField(_('dirección'), blank=True)
    notes = models.TextField(_('notas'), blank=True)
    is_active = models.BooleanField(_('activo'), default=True)

    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)

    class Meta:
        verbose_name = _('proveedor')
        verbose_name_plural = _('proveedores')
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Productos/materiales del inventario odontológico.
    """

    class Unit(models.TextChoices):
        UNIT = 'unit', _('Unidad')
        BOX = 'box', _('Caja')
        PACK = 'pack', _('Paquete')
        TUBE = 'tube', _('Tubo')
        BOTTLE = 'bottle', _('Frasco')
        ML = 'ml', _('Mililitros')
        GR = 'gr', _('Gramos')
        KIT = 'kit', _('Kit')

    # Identificación
    code = models.CharField(
        _('código'),
        max_length=50,
        unique=True,
        help_text=_('Código interno o SKU')
    )
    name = models.CharField(_('nombre'), max_length=200)
    description = models.TextField(_('descripción'), blank=True)
    brand = models.CharField(_('marca'), max_length=100, blank=True)

    # Clasificación
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('categoría'),
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('proveedor'),
    )

    # Unidades y stock
    unit = models.CharField(
        _('unidad de medida'),
        max_length=20,
        choices=Unit.choices,
        default=Unit.UNIT,
    )
    current_stock = models.DecimalField(
        _('stock actual'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
    )
    minimum_stock = models.DecimalField(
        _('stock mínimo'),
        max_digits=10,
        decimal_places=2,
        default=5,
        validators=[MinValueValidator(Decimal('0'))],
        help_text=_('Alerta cuando el stock sea igual o menor')
    )
    maximum_stock = models.DecimalField(
        _('stock máximo'),
        max_digits=10,
        decimal_places=2,
        default=100,
        validators=[MinValueValidator(Decimal('0'))],
        help_text=_('Cantidad máxima recomendada')
    )

    # Precios
    purchase_price = models.DecimalField(
        _('precio de compra'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
    )
    sale_price = models.DecimalField(
        _('precio de venta'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text=_('Precio si se vende al paciente')
    )

    # Control
    expiration_date = models.DateField(
        _('fecha de vencimiento'),
        null=True,
        blank=True,
    )
    location = models.CharField(
        _('ubicación'),
        max_length=100,
        blank=True,
        help_text=_('Ej: Estante A, Gaveta 3')
    )
    is_active = models.BooleanField(_('activo'), default=True)

    # Relación con consultorio
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('consultorio'),
        null=True,
        blank=True,
    )

    # Timestamps
    created_at = models.DateTimeField(_('creado'), auto_now_add=True)
    updated_at = models.DateTimeField(_('actualizado'), auto_now=True)

    class Meta:
        verbose_name = _('producto')
        verbose_name_plural = _('productos')
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return f'{self.code} - {self.name}'

    @property
    def is_low_stock(self):
        """Indica si el stock está bajo el mínimo."""
        return self.current_stock <= self.minimum_stock

    @property
    def is_out_of_stock(self):
        """Indica si no hay stock."""
        return self.current_stock <= 0

    @property
    def is_expiring_soon(self):
        """Indica si el producto vence en los próximos 30 días."""
        if not self.expiration_date:
            return False
        from datetime import timedelta
        return self.expiration_date <= timezone.now().date() + timedelta(days=30)

    @property
    def is_expired(self):
        """Indica si el producto ya venció."""
        if not self.expiration_date:
            return False
        return self.expiration_date < timezone.now().date()

    @property
    def stock_status(self):
        """Estado del stock para UI."""
        if self.is_out_of_stock:
            return {'label': 'Sin stock', 'color': 'danger', 'icon': 'x-circle'}
        elif self.is_low_stock:
            return {'label': 'Stock bajo', 'color': 'warning', 'icon': 'exclamation-triangle'}
        else:
            return {'label': 'Disponible', 'color': 'success', 'icon': 'check-circle'}

    @property
    def stock_percentage(self):
        """Porcentaje de stock respecto al máximo."""
        if self.maximum_stock <= 0:
            return 100
        return min(100, int((self.current_stock / self.maximum_stock) * 100))

    def add_stock(self, quantity, user=None, notes='', cost=None):
        """Agregar stock (entrada)."""
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")

        movement = StockMovement.objects.create(
            product=self,
            movement_type=StockMovement.MovementType.IN,
            quantity=quantity,
            unit_cost=cost or self.purchase_price,
            notes=notes,
            created_by=user,
        )

        self.current_stock += Decimal(str(quantity))
        if cost:
            self.purchase_price = cost
        self.save()

        return movement

    def remove_stock(self, quantity, user=None, notes='', reason='use'):
        """Retirar stock (salida)."""
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        if quantity > self.current_stock:
            raise ValueError("Stock insuficiente")

        movement = StockMovement.objects.create(
            product=self,
            movement_type=StockMovement.MovementType.OUT,
            quantity=quantity,
            unit_cost=self.purchase_price,
            notes=notes,
            reason=reason,
            created_by=user,
        )

        self.current_stock -= Decimal(str(quantity))
        self.save()

        return movement

    def adjust_stock(self, new_quantity, user=None, notes=''):
        """Ajustar stock (inventario físico)."""
        difference = Decimal(str(new_quantity)) - self.current_stock

        if difference == 0:
            return None

        movement = StockMovement.objects.create(
            product=self,
            movement_type=StockMovement.MovementType.ADJUSTMENT,
            quantity=abs(difference),
            unit_cost=self.purchase_price,
            notes=notes or f'Ajuste de inventario: {self.current_stock} → {new_quantity}',
            created_by=user,
        )

        self.current_stock = Decimal(str(new_quantity))
        self.save()

        return movement


class StockMovement(models.Model):
    """
    Registro de movimientos de inventario.
    """

    class MovementType(models.TextChoices):
        IN = 'in', _('Entrada')
        OUT = 'out', _('Salida')
        ADJUSTMENT = 'adjustment', _('Ajuste')
        RETURN = 'return', _('Devolución')
        EXPIRED = 'expired', _('Vencido')
        DAMAGED = 'damaged', _('Dañado')

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name=_('producto'),
    )
    movement_type = models.CharField(
        _('tipo'),
        max_length=20,
        choices=MovementType.choices,
    )
    quantity = models.DecimalField(
        _('cantidad'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    unit_cost = models.DecimalField(
        _('costo unitario'),
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    reason = models.CharField(
        _('motivo'),
        max_length=100,
        blank=True,
        help_text=_('Ej: Uso en procedimiento, Compra, Pérdida')
    )
    notes = models.TextField(_('notas'), blank=True)

    # Referencia opcional a cita (si se usó en un procedimiento)
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_movements',
        verbose_name=_('cita'),
    )

    # Auditoría
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('registrado por'),
    )
    created_at = models.DateTimeField(_('fecha'), auto_now_add=True)

    class Meta:
        verbose_name = _('movimiento de stock')
        verbose_name_plural = _('movimientos de stock')
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.movement_type == self.MovementType.IN else '-'
        return f'{self.product.name}: {sign}{self.quantity} ({self.get_movement_type_display()})'

    @property
    def total_cost(self):
        return self.quantity * self.unit_cost

    @property
    def is_entry(self):
        return self.movement_type in [self.MovementType.IN, self.MovementType.RETURN]

    @property
    def movement_color(self):
        colors = {
            self.MovementType.IN: 'success',
            self.MovementType.OUT: 'primary',
            self.MovementType.ADJUSTMENT: 'info',
            self.MovementType.RETURN: 'warning',
            self.MovementType.EXPIRED: 'danger',
            self.MovementType.DAMAGED: 'danger',
        }
        return colors.get(self.movement_type, 'secondary')
