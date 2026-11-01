from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from accounts.roles import ADMIN, MANAGER, STAFF
from inventory.models import Component


class InventoryDashboardTests(TestCase):
    def setUp(self):
        self.url = reverse("reports:dashboard")
        self.users = {}
        for username, role in (("dashboard-admin", ADMIN), ("dashboard-manager", MANAGER), ("dashboard-staff", STAFF)):
            user = get_user_model().objects.create_user(username=username, password="test-password-123")
            user.groups.add(Group.objects.get(name=role))
            self.users[role] = user

    def create_component(self, component_id, quantity, minimum_stock, *, active=True):
        return Component.objects.create(
            component_id=component_id,
            name=f"Component {component_id}",
            category="Sensors",
            price=Decimal("2.00"),
            quantity=quantity,
            minimum_stock=minimum_stock,
            is_active=active,
        )

    def test_anonymous_user_is_sent_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.url}")

    def test_staff_cannot_view_manager_dashboard(self):
        self.client.force_login(self.users[STAFF])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertNotContains(self.client.get(reverse("inventory:list")), reverse("reports:dashboard"))

    def test_manager_and_administrator_can_view_dashboard(self):
        for role in (MANAGER, ADMIN):
            with self.subTest(role=role):
                self.client.force_login(self.users[role])
                self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_totals_use_active_inventory_records_and_stock_units(self):
        self.create_component("DASH-LOW", 4, 5)
        self.create_component("DASH-BOUNDARY", 5, 5)
        self.create_component("DASH-AVAILABLE", 9, 5)
        self.create_component("DASH-INACTIVE", 100, 1, active=False)
        self.client.force_login(self.users[MANAGER])

        response = self.client.get(self.url)

        self.assertEqual(response.context["total_components"], 3)
        self.assertEqual(response.context["available_stock"], 18)
        self.assertEqual(response.context["low_stock_count"], 2)
        self.assertQuerySetEqual(
            response.context["low_stock_components"],
            ["DASH-BOUNDARY", "DASH-LOW"],
            transform=lambda component: component.component_id,
        )

    def test_summary_cards_and_low_stock_highlighting_show_live_values(self):
        self.create_component("DASH-BELOW", 2, 5)
        self.create_component("DASH-AT", 5, 5)
        self.create_component("DASH-ABOVE", 6, 5)
        self.client.force_login(self.users[MANAGER])

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "reports/dashboard.html")
        self.assertContains(response, "Total components")
        self.assertContains(response, "Available stock units")
        self.assertContains(response, "Low-stock components")
        self.assertContains(response, "13")
        self.assertContains(response, "DASH-BELOW")
        self.assertContains(response, "DASH-AT")
        self.assertNotContains(response, "DASH-ABOVE")

    def test_dashboard_reflects_inventory_changes_on_next_request(self):
        component = self.create_component("DASH-CHANGE", 20, 5)
        self.client.force_login(self.users[MANAGER])
        before = self.client.get(self.url)
        self.assertEqual(before.context["available_stock"], 20)
        self.assertEqual(before.context["low_stock_count"], 0)

        component.quantity = 5
        component.save(update_fields=["quantity", "updated_at"])
        after = self.client.get(self.url)

        self.assertEqual(after.context["available_stock"], 5)
        self.assertEqual(after.context["low_stock_count"], 1)
