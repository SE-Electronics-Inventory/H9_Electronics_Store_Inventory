"""
Inventory Models (ESIM-F-003, ESIM-F-004, ESIM-F-008, ESIM-F-009, ESIM-F-013)
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Component(models.Model):
    """
    Electronic Component inventory record.
    Represents an inventory item stored in the system.
    """
    CATEGORY_CHOICES = [
        ("Microcontrollers", "Microcontrollers & Boards"),
        ("Sensors", "Sensors & Modules"),
        ("Passives", "Passive Components (Resistors/Capacitors)"),
        ("Semiconductors", "Semiconductors (Diodes/ICs/Transistors)"),
        ("Optoelectronics", "Optoelectronics & Displays"),
        ("Power", "Power Supplies & Batteries"),
        ("Connectors", "Connectors, Cables & Relays"),
        ("Other", "Other Electronic Parts"),
    ]

    component_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Component ID",
        help_text="Unique component identifier (e.g., RES-10K-001, ESP32-DEV-01)"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Component Name",
        help_text="Descriptive component title"
    )
    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        default="Other",
        verbose_name="Category"
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description / Specs"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Unit Price (INR)"
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantity in Stock"
    )
    minimum_stock = models.PositiveIntegerField(
        default=10,
        verbose_name="Minimum Stock Level",
        help_text="Threshold below which item is flagged as Low Stock"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active in Inventory",
        help_text="Soft-delete status (FR-07)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["component_id"]
        verbose_name = "Component"
        verbose_name_plural = "Components"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=Decimal("0.00")),
                name="component_price_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=0),
                name="component_quantity_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(minimum_stock__gte=0),
                name="component_minimum_stock_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.component_id} - {self.name} ({self.quantity} in stock)"

    @property
    def availability(self):
        """
        Calculate stock availability status (ESIM-F-008 / TC-AVAIL-01):
        - Out of Stock: quantity <= 0
        - Low Stock: 0 < quantity <= minimum_stock
        - In Stock: quantity > minimum_stock
        """
        if self.quantity <= 0:
            return "Out of Stock"
        elif self.quantity <= self.minimum_stock:
            return "Low Stock"
        return "In Stock"

    @property
    def is_low_stock(self):
        """ESIM-F-009: flag whether component is at or below minimum threshold."""
        return self.quantity <= self.minimum_stock
