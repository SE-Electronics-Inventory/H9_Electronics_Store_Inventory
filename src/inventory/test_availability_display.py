"""FR-08 tests for availability labels rendered in the inventory list."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Component


class AvailabilityDisplayTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="availability-viewer",
            password="test-password",
        )
        self.client.force_login(user)

    def test_list_displays_status_for_zero_below_equal_and_above_threshold(self):
        cases = [
            ("AVAIL-ZERO", 0, 5, "Out of Stock", "badge-out-of-stock"),
            ("AVAIL-BELOW", 2, 5, "Low Stock", "badge-low-stock"),
            ("AVAIL-EQUAL", 5, 5, "Low Stock", "badge-low-stock"),
            ("AVAIL-ABOVE", 6, 5, "In Stock", "badge-in-stock"),
        ]
        for component_id, quantity, minimum_stock, _status, _badge in cases:
            Component.objects.create(
                component_id=component_id,
                name=f"Component {component_id}",
                price=Decimal("10.00"),
                quantity=quantity,
                minimum_stock=minimum_stock,
            )

        response = self.client.get(reverse("inventory:list"))

        self.assertEqual(response.status_code, 200)
        for component_id, _quantity, _minimum_stock, status, badge in cases:
            with self.subTest(component_id=component_id):
                self.assertContains(response, component_id)
                self.assertContains(response, status)
                self.assertContains(response, f'class="badge-status {badge}"')
