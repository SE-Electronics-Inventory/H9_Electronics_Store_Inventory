from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from accounts.roles import ADMIN, STAFF
from inventory.models import Component


class InventoryUsabilityTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(username="usable-admin", password="Store@12345")
        self.admin.groups.add(Group.objects.get(name=ADMIN))
        self.staff = get_user_model().objects.create_user(username="usable-staff", password="Store@12345")
        self.staff.groups.add(Group.objects.get(name=STAFF))

    def test_login_fields_have_autocomplete_and_invalid_login_has_accessible_feedback(self):
        login_url = reverse("accounts:login")
        page = self.client.get(login_url)
        self.assertContains(page, 'autocomplete="username"')
        self.assertContains(page, 'autocomplete="current-password"')

        failed = self.client.post(login_url, {"username": "usable-admin", "password": "wrong"})
        self.assertContains(failed, 'role="alert"')
        self.assertContains(failed, "Invalid username or password")

    def test_inventory_search_is_labelled_and_reports_results(self):
        Component.objects.create(component_id="UX-RES-1", name="Precision resistor", category="Passives", price=Decimal("1.25"), quantity=20, minimum_stock=5)
        Component.objects.create(component_id="UX-SEN-1", name="Temperature sensor", category="Sensors", price=Decimal("3.50"), quantity=3, minimum_stock=5)
        self.client.force_login(self.staff)

        response = self.client.get(reverse("inventory:list"), {"q": "temperature"})

        self.assertContains(response, 'role="search"')
        self.assertContains(response, "Search components by ID or name")
        self.assertContains(response, 'role="status"')
        self.assertContains(response, "UX-SEN-1")
        self.assertNotContains(response, "UX-RES-1")
        self.assertContains(response, "1 match")

    def test_no_results_has_clear_filters_action(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("inventory:list"), {"q": "missing-part"})

        self.assertContains(response, "No components match your search")
        self.assertContains(response, "Clear Filters")

    def test_inventory_administrator_sees_permitted_add_action(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("inventory:list"))

        self.assertContains(response, reverse("inventory:add"))
        self.assertContains(response, "+ Add New Component")

    def test_staff_has_navigation_and_search_but_no_inventory_write_action(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("inventory:list"))

        self.assertContains(response, "Inventory")
        self.assertContains(response, "Low Stock")
        self.assertNotContains(response, reverse("inventory:add"))
        denied = self.client.post(reverse("inventory:add"), {"component_id": "UX-FORBIDDEN"})
        self.assertEqual(denied.status_code, 403)
        self.assertFalse(Component.objects.filter(component_id="UX-FORBIDDEN").exists())

    def test_permitted_add_operation_returns_success_feedback(self):
        self.client.force_login(self.admin)

        response = self.client.post(reverse("inventory:add"), {
            "component_id": "UX-ADD-1",
            "name": "Test component",
            "category": "Sensors",
            "description": "",
            "price": "5.00",
            "quantity": "3",
            "minimum_stock": "2",
            "is_active": "on",
        }, follow=True)

        self.assertContains(response, "Component added successfully")
        self.assertTrue(Component.objects.filter(component_id="UX-ADD-1").exists())

    def test_invalid_add_keeps_user_data_and_shows_field_error(self):
        self.client.force_login(self.admin)

        response = self.client.post(reverse("inventory:add"), {
            "component_id": "UX-INVALID-1",
            "name": "   ",
            "category": "Sensors",
            "description": "",
            "price": "5.00",
            "quantity": "3",
            "minimum_stock": "2",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertFalse(Component.objects.filter(component_id="UX-INVALID-1").exists())
