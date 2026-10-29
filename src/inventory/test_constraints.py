"""Database-level integrity checks for inventory component values."""

from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Component


class ComponentDatabaseConstraintTests(TestCase):
    """Verify invalid values are rejected even when model validation is bypassed."""

    def component_data(self, **overrides):
        data = {
            "component_id": "CONSTRAINT-001",
            "name": "Constraint Test Component",
            "price": Decimal("10.00"),
            "quantity": 1,
            "minimum_stock": 1,
        }
        data.update(overrides)
        return data

    def assert_database_rejects(self, **overrides):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Component.objects.create(**self.component_data(**overrides))

    def test_negative_price_is_rejected_by_database(self):
        self.assert_database_rejects(price=Decimal("-1.00"))

    def test_negative_quantity_is_rejected_by_database(self):
        self.assert_database_rejects(quantity=-1)

    def test_negative_minimum_stock_is_rejected_by_database(self):
        self.assert_database_rejects(minimum_stock=-1)
