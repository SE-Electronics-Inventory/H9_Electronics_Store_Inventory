"""Tests for the FR-09 low-stock components page."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .models import Component


class LowStockListTests(TestCase):
    def setUp(self):
        manager_group, _ = Group.objects.get_or_create(name="Store Manager")
        self.manager = get_user_model().objects.create_user(
            username="low-stock-manager",
            password="test-password-123",
        )
        self.manager.groups.add(manager_group)
        self.client.force_login(self.manager)
        self.url = reverse("inventory:low_stock")

    def create_component(self, component_id, quantity, minimum_stock, *, is_active=True):
        return Component.objects.create(
            component_id=component_id,
            name=f"Component {component_id}",
            category="Sensors",
            price=Decimal("10.00"),
            quantity=quantity,
            minimum_stock=minimum_stock,
            is_active=is_active,
        )

    def test_lists_below_threshold_and_out_of_stock_components(self):
        self.create_component("LOW-001", quantity=2, minimum_stock=5)
        self.create_component("ZERO-001", quantity=0, minimum_stock=5)
        self.create_component("NORMAL-001", quantity=6, minimum_stock=5)
        self.create_component("INACTIVE-001", quantity=1, minimum_stock=5, is_active=False)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory/low_stock_list.html")
        self.assertContains(response, "LOW-001")
        self.assertContains(response, "ZERO-001")
        self.assertNotContains(response, "NORMAL-001")
        self.assertNotContains(response, "INACTIVE-001")

    def test_threshold_boundary_includes_equal_and_excludes_above(self):
        self.create_component("BOUNDARY-EQUAL", quantity=5, minimum_stock=5)
        self.create_component("BOUNDARY-ABOVE", quantity=6, minimum_stock=5)

        response = self.client.get(self.url)

        self.assertContains(response, "BOUNDARY-EQUAL")
        self.assertNotContains(response, "BOUNDARY-ABOVE")

    def test_empty_low_stock_list_has_clear_message(self):
        self.create_component("NORMAL-ONLY", quantity=8, minimum_stock=5)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No low-stock components")
        self.assertNotContains(response, "NORMAL-ONLY")

    def test_list_updates_after_stock_quantity_changes(self):
        component = self.create_component("CHANGING-STOCK", quantity=2, minimum_stock=5)

        low_stock_response = self.client.get(self.url)
        self.assertContains(low_stock_response, "CHANGING-STOCK")

        component.quantity = 6
        component.save(update_fields=["quantity"])

        normal_stock_response = self.client.get(self.url)
        self.assertNotContains(normal_stock_response, "CHANGING-STOCK")
        self.assertContains(normal_stock_response, "No low-stock components")

    def test_low_stock_page_requires_login(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.url}",
        )
