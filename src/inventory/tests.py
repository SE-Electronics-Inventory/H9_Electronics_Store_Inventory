"""
Tests for Component Inventory (ESIM-F-004: TC-INV-02, ESIM-F-008: TC-AVAIL-01)
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from decimal import Decimal
from .forms import ComponentForm
from .models import Component


class ComponentModelTests(TestCase):
    """Unit tests for Component model behavior and availability calculation."""

    def test_availability_calculation_rules(self):
        """
        TC-AVAIL-01: Availability matches the documented rule for quantities:
        - above minimum_stock -> In Stock
        - equal to minimum_stock -> Low Stock
        - below minimum_stock but > 0 -> Low Stock
        - equal to 0 -> Out of Stock
        """
        in_stock_item = Component.objects.create(
            component_id="TEST-001",
            name="In Stock Component",
            category="Passives",
            price=Decimal("10.00"),
            quantity=25,
            minimum_stock=10,
        )
        self.assertEqual(in_stock_item.availability, "In Stock")
        self.assertFalse(in_stock_item.is_low_stock)

        at_min_item = Component.objects.create(
            component_id="TEST-002",
            name="At Minimum Component",
            category="Sensors",
            price=Decimal("50.00"),
            quantity=10,
            minimum_stock=10,
        )
        self.assertEqual(at_min_item.availability, "Low Stock")
        self.assertTrue(at_min_item.is_low_stock)

        below_min_item = Component.objects.create(
            component_id="TEST-003",
            name="Below Minimum Component",
            category="Sensors",
            price=Decimal("50.00"),
            quantity=5,
            minimum_stock=10,
        )
        self.assertEqual(below_min_item.availability, "Low Stock")
        self.assertTrue(below_min_item.is_low_stock)

        out_of_stock_item = Component.objects.create(
            component_id="TEST-004",
            name="Out of Stock Component",
            category="Power",
            price=Decimal("150.00"),
            quantity=0,
            minimum_stock=5,
        )
        self.assertEqual(out_of_stock_item.availability, "Out of Stock")
        self.assertTrue(out_of_stock_item.is_low_stock)

    def test_component_string_representation(self):
        """Verifies readable string output of Component instance."""
        comp = Component.objects.create(
            component_id="RES-01",
            name="100 Ohm Resistor",
            price=Decimal("1.50"),
            quantity=20,
            minimum_stock=5,
        )
        self.assertIn("RES-01", str(comp))
        self.assertIn("100 Ohm Resistor", str(comp))


class InventoryListViewTests(TestCase):
    """Integration & view tests for FR-04: View Component Inventory."""

    def setUp(self):
        self.client = Client()
        # Inventory pages need a logged-in user (FR-01)
        self.user = get_user_model().objects.create_user(username="tester", password="Test@12345")
        self.client.force_login(self.user)
        self.url = reverse("inventory:list")

        # Create components matching TC-INV-02 dataset
        self.comp1 = Component.objects.create(
            component_id="CMP-101",
            name="Microcontroller ATmega328P",
            category="Microcontrollers",
            description="8-bit AVR microcontroller",
            price=Decimal("180.00"),
            quantity=15,
            minimum_stock=5,
        )
        self.comp2 = Component.objects.create(
            component_id="CMP-102",
            name="Ultrasonic Sensor HC-SR04",
            category="Sensors",
            description="Distance sensor module",
            price=Decimal("75.50"),
            quantity=3,
            minimum_stock=10,
        )
        self.inactive_comp = Component.objects.create(
            component_id="CMP-999",
            name="Deactivated Old Component",
            price=Decimal("5.00"),
            quantity=10,
            minimum_stock=5,
            is_active=False,
        )

    def test_view_status_code_and_template(self):
        """Inventory list endpoint returns 200 OK and uses the proper template."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inventory/component_list.html")
        self.assertTemplateUsed(response, "base.html")

    def test_all_stored_components_displayed(self):
        """
        TC-INV-02: Every active component in the database is retrievable and displayed.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # Check content contains component details
        self.assertContains(response, "CMP-101")
        self.assertContains(response, "Microcontroller ATmega328P")
        self.assertContains(response, "180.00")
        self.assertContains(response, "15")
        self.assertContains(response, "In Stock")

        self.assertContains(response, "CMP-102")
        self.assertContains(response, "Ultrasonic Sensor HC-SR04")
        self.assertContains(response, "75.50")
        self.assertContains(response, "3")
        self.assertContains(response, "Low Stock")

        # Inactive components should be excluded from active inventory list
        self.assertNotContains(response, "CMP-999")
        self.assertNotContains(response, "Deactivated Old Component")

    def test_empty_inventory_message(self):
        """When no components exist, clear feedback message is displayed."""
        Component.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No components found")


class InventoryPersistenceAndValidationTests(TestCase):
    """TC-DATA-01 and TC-VAL-01 for database-backed inventory writes."""

    def setUp(self):
        self.admin_group, _ = Group.objects.get_or_create(
            name="Inventory Administrator"
        )
        self.admin = get_user_model().objects.create_user(
            username="persistence-admin",
            password="test-password-123",
        )
        self.admin.groups.add(self.admin_group)
        self.client.force_login(self.admin)

    def valid_data(self, **overrides):
        data = {
            "component_id": "PERSIST-001",
            "name": "Persistent Sensor",
            "category": "Sensors",
            "description": "Stored in the inventory database",
            "price": "125.50",
            "quantity": "12",
            "minimum_stock": "3",
            "is_active": "on",
        }
        data.update(overrides)
        return data

    def test_valid_component_is_saved_and_retrieved_from_database(self):
        response = self.client.post(
            reverse("inventory:add"), data=self.valid_data()
        )

        self.assertRedirects(response, reverse("inventory:list"))
        self.assertTrue(Component.objects.filter(component_id="PERSIST-001").exists())

        response = self.client.get(reverse("inventory:list"))
        self.assertContains(response, "PERSIST-001")
        self.assertContains(response, "Persistent Sensor")

    def test_component_update_is_saved_and_retrieved_from_database(self):
        component = Component.objects.create(
            component_id="PERSIST-001",
            name="Original Sensor",
            price=Decimal("100.00"),
            quantity=4,
        )

        response = self.client.post(
            reverse("inventory:edit", args=[component.pk]),
            data=self.valid_data(name="Updated Sensor", quantity="15"),
        )

        self.assertRedirects(response, reverse("inventory:list"))
        component.refresh_from_db()
        self.assertEqual(component.name, "Updated Sensor")
        self.assertEqual(component.quantity, 15)

    def test_missing_mandatory_fields_are_rejected_without_persisting(self):
        form = ComponentForm(
            self.valid_data(component_id="", name="", price="")
        )

        self.assertFalse(form.is_valid())
        self.assertIn("component_id", form.errors)
        self.assertIn("name", form.errors)
        self.assertIn("price", form.errors)
        self.assertEqual(Component.objects.count(), 0)

    def test_duplicate_component_id_is_rejected_without_persisting(self):
        Component.objects.create(
            component_id="PERSIST-001",
            name="Existing Component",
            price=Decimal("10.00"),
        )

        response = self.client.post(
            reverse("inventory:add"), data=self.valid_data()
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("component_id", response.context["form"].errors)
        self.assertEqual(Component.objects.count(), 1)

    def test_negative_quantity_is_rejected_without_persisting(self):
        response = self.client.post(
            reverse("inventory:add"), data=self.valid_data(quantity="-1")
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("quantity", response.context["form"].errors)
        self.assertFalse(Component.objects.exists())

    def test_invalid_prices_are_rejected_without_persisting(self):
        for price in ("-1.00", "not-a-price"):
            with self.subTest(price=price):
                response = self.client.post(
                    reverse("inventory:add"), data=self.valid_data(price=price)
                )

                self.assertEqual(response.status_code, 200)
                self.assertIn("price", response.context["form"].errors)
                self.assertFalse(Component.objects.exists())

    def test_invalid_update_does_not_change_existing_record(self):
        component = Component.objects.create(
            component_id="PERSIST-001",
            name="Existing Component",
            price=Decimal("10.00"),
            quantity=5,
        )

        response = self.client.post(
            reverse("inventory:edit", args=[component.pk]),
            data=self.valid_data(component_id="", quantity="-5", price="-1"),
        )

        self.assertEqual(response.status_code, 200)
        component.refresh_from_db()
        self.assertEqual(component.component_id, "PERSIST-001")
        self.assertEqual(component.name, "Existing Component")
        self.assertEqual(component.price, Decimal("10.00"))
        self.assertEqual(component.quantity, 5)


class SearchAndFilterTests(TestCase):
    """
    Test suite for FR-05: Search and Filter Components (ESIM-F-005 / TC-SEARCH-01).
    Covers User Story #51 (search by ID or name) and User Story #52 (filter by category).
    """

    def setUp(self):
        self.client = Client()
        # Inventory pages need a logged-in user (FR-01)
        self.user = get_user_model().objects.create_user(username="tester", password="Test@12345")
        self.client.force_login(self.user)
        self.url = reverse("inventory:list")

        self.c1 = Component.objects.create(
            component_id="ESP32-WROOM",
            name="ESP32 Wi-Fi Bluetooth Module",
            category="Microcontrollers",
            price=Decimal("350.00"),
            quantity=20,
            minimum_stock=5,
        )
        self.c2 = Component.objects.create(
            component_id="ARD-NANO",
            name="Arduino Nano V3",
            category="Microcontrollers",
            price=Decimal("250.00"),
            quantity=15,
            minimum_stock=5,
        )
        self.c3 = Component.objects.create(
            component_id="SEN-DHT22",
            name="DHT22 High-Accuracy Temp Sensor",
            category="Sensors",
            price=Decimal("180.00"),
            quantity=8,
            minimum_stock=10,
        )
        self.c4 = Component.objects.create(
            component_id="RES-10K",
            name="10k Ohm Resistor Pack",
            category="Passives",
            price=Decimal("25.00"),
            quantity=100,
            minimum_stock=20,
        )
        self.c_inactive = Component.objects.create(
            component_id="SEN-OLD-01",
            name="Old Deactivated Sensor",
            category="Sensors",
            price=Decimal("50.00"),
            quantity=5,
            is_active=False,
        )

    def test_search_by_component_id(self):
        """User Story #51: Typing an ID shows only matching components (case-insensitive)."""
        response = self.client.get(self.url, {"q": "esp32"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ESP32-WROOM")
        self.assertNotContains(response, "ARD-NANO")
        self.assertNotContains(response, "SEN-DHT22")
        self.assertNotContains(response, "RES-10K")

    def test_search_by_component_name(self):
        """User Story #51: Typing a name shows only matching components."""
        response = self.client.get(self.url, {"q": "resistor"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "RES-10K")
        self.assertContains(response, "10k Ohm Resistor Pack")
        self.assertNotContains(response, "ESP32-WROOM")
        self.assertNotContains(response, "ARD-NANO")

    def test_filter_by_category(self):
        """User Story #52: Choosing a category shows only that category."""
        response = self.client.get(self.url, {"category": "Microcontrollers"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ESP32-WROOM")
        self.assertContains(response, "ARD-NANO")
        self.assertNotContains(response, "SEN-DHT22")
        self.assertNotContains(response, "RES-10K")

    def test_search_and_category_filter_combined(self):
        """TC-SEARCH-01: ID/name search and category filter work together."""
        # Search for 'nano' in 'Microcontrollers'
        response = self.client.get(self.url, {"q": "nano", "category": "Microcontrollers"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ARD-NANO")
        self.assertNotContains(response, "ESP32-WROOM")
        self.assertNotContains(response, "SEN-DHT22")

        # Search for 'nano' in 'Sensors' -> no match
        response_empty = self.client.get(self.url, {"q": "nano", "category": "Sensors"})
        self.assertEqual(response_empty.status_code, 200)
        self.assertContains(response_empty, "No components found")
        self.assertNotContains(response_empty, "ARD-NANO")

    def test_no_match_shows_no_components_found(self):
        """TC-SEARCH-01 / #52: If nothing matches, 'No components found' is shown."""
        response = self.client.get(self.url, {"q": "NonExistentPartXYZ"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No components found")
        self.assertEqual(response.context["total_components"], 0)

    def test_inactive_components_excluded_from_search(self):
        """Deactivated components are excluded from search results."""
        response = self.client.get(self.url, {"q": "Deactivated"})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "SEN-OLD-01")
        self.assertContains(response, "No components found")


class ComponentAddAuthorizationTests(TestCase):
    def setUp(self):
        self.url = reverse("inventory:add")
        self.admin_group, _ = Group.objects.get_or_create(
            name="Inventory Administrator"
        )
        self.admin = get_user_model().objects.create_user(
            username="inventory-admin",
            password="test-password-123",
        )
        self.admin.groups.add(self.admin_group)

    def valid_data(self, **overrides):
        data = {
            "component_id": "NEW-001",
            "name": "New Sensor",
            "category": "Sensors",
            "description": "Temperature sensor",
            "price": "12.50",
            "quantity": "8",
            "minimum_stock": "3",
            "is_active": "on",
        }
        data.update(overrides)
        return data

    def test_inventory_administrator_can_add_component(self):
        self.client.force_login(self.admin)

        response = self.client.post(self.url, self.valid_data())

        self.assertRedirects(response, reverse("inventory:list"))
        component = Component.objects.get(component_id="NEW-001")
        self.assertEqual(component.name, "New Sensor")
        self.assertEqual(component.price, Decimal("12.50"))
        self.assertEqual(component.quantity, 8)
        self.assertTrue(component.is_active)

    def test_invalid_component_is_not_saved(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            self.url,
            self.valid_data(price="-1.00", quantity="-2"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Component.objects.count(), 0)
        self.assertIn("price", response.context["form"].errors)
        self.assertIn("quantity", response.context["form"].errors)

    def test_add_requires_login(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={self.url}",
        )

    def test_add_is_forbidden_for_users_outside_admin_group(self):
        regular_user = get_user_model().objects.create_user(
            username="regular-user",
            password="test-password-123",
        )
        self.client.force_login(regular_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)
