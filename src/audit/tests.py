"""
Tests for Inventory Change Tracking & Audit Trail (FR-16: ESIM-F-016 / TC-AUD-01)
Covers User Story #57 (record every inventory change) and User Story #58 (change history page).
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse

from accounts.roles import ADMIN, MANAGER, STAFF
from audit.models import ChangeLog, log_change
from inventory.models import Component


class ChangeLogModelTests(TestCase):
    """Unit tests for ChangeLog model and log_change helper."""

    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username="admin_logger", password="Password@123"
        )
        self.component = Component.objects.create(
            component_id="LOG-001",
            name="Logging Resistor",
            category="Passives",
            price=Decimal("5.00"),
            quantity=50,
            minimum_stock=10,
        )

    def test_log_change_creates_record(self):
        """TC-AUD-01: A supported inventory change creates the defined audit information."""
        log = log_change(
            self.component,
            action="ADD",
            user=self.admin,
            details="Initial component addition"
        )
        self.assertEqual(ChangeLog.objects.count(), 1)
        self.assertEqual(log.component_id, "LOG-001")
        self.assertEqual(log.component_name, "Logging Resistor")
        self.assertEqual(log.action, "ADD")
        self.assertEqual(log.user, self.admin)
        self.assertEqual(log.details, "Initial component addition")
        self.assertIsNotNone(log.timestamp)

    def test_log_change_str_representation(self):
        """Verifies readable string output of ChangeLog instance."""
        log = log_change(self.component, action="EDIT", user=self.admin)
        self.assertIn("LOG-001", str(log))
        self.assertIn("Updated", str(log))
        self.assertIn("admin_logger", str(log))


class InventoryChangeTrackingIntegrationTests(TestCase):
    """
    Integration tests verifying that add, edit, and delete operations
    automatically generate audit log entries (Story #57 / TC-AUD-01).
    """

    def setUp(self):
        self.client = Client()
        self.admin_group, _ = Group.objects.get_or_create(name=ADMIN)
        self.admin = get_user_model().objects.create_user(
            username="inventory_admin_auditor", password="Password@123"
        )
        self.admin.groups.add(self.admin_group)
        self.client.force_login(self.admin)

    def test_adding_component_creates_audit_log(self):
        """Story #57: Adding a component creates an 'ADD' change log entry with user and time."""
        add_url = reverse("inventory:add")
        data = {
            "component_id": "AUD-ADD-01",
            "name": "Audit Test Capacitor",
            "category": "Passives",
            "description": "Electrolytic 10uF",
            "price": "15.00",
            "quantity": "40",
            "minimum_stock": "10",
        }
        response = self.client.post(add_url, data)
        self.assertRedirects(response, reverse("inventory:list"))

        # Verify audit log created
        log = ChangeLog.objects.filter(component_id="AUD-ADD-01").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.action, "ADD")
        self.assertEqual(log.component_name, "Audit Test Capacitor")
        self.assertEqual(log.user, self.admin)
        self.assertIn("40", log.details)

    def test_editing_component_creates_audit_log(self):
        """Story #57: Updating a component creates an 'EDIT' change log entry with user and time."""
        component = Component.objects.create(
            component_id="AUD-EDIT-01",
            name="Audit Edit Sensor",
            category="Sensors",
            price=Decimal("120.00"),
            quantity=15,
            minimum_stock=5,
        )
        edit_url = reverse("inventory:edit", args=[component.pk])
        data = {
            "component_id": "AUD-EDIT-01",
            "name": "Audit Edit Sensor Updated",
            "category": "Sensors",
            "description": "Updated sensor specs",
            "price": "135.00",
            "quantity": "25",
            "minimum_stock": "5",
        }
        response = self.client.post(edit_url, data)
        self.assertRedirects(response, reverse("inventory:list"))

        log = ChangeLog.objects.filter(component_id="AUD-EDIT-01", action="EDIT").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.action, "EDIT")
        self.assertEqual(log.user, self.admin)
        self.assertIn("25", log.details)

    def test_deactivating_component_creates_audit_log(self):
        """Story #57: Deactivating a component creates a 'DELETE' change log entry with user and time."""
        component = Component.objects.create(
            component_id="AUD-DEL-01",
            name="Audit Deactivate Module",
            category="Semiconductors",
            price=Decimal("75.00"),
            quantity=8,
            minimum_stock=2,
        )
        delete_url = reverse("inventory:delete", args=[component.pk])
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("inventory:list"))

        log = ChangeLog.objects.filter(component_id="AUD-DEL-01", action="DELETE").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.action, "DELETE")
        self.assertEqual(log.user, self.admin)
        self.assertIn("Deactivated", log.details)


class AuditHistoryPageTests(TestCase):
    """
    Tests for the Change History Page (Story #58 / TC-AUD-01).
    """

    def setUp(self):
        self.client = Client()
        self.history_url = reverse("audit:log_list")

        self.admin_group, _ = Group.objects.get_or_create(name=ADMIN)
        self.admin = get_user_model().objects.create_user(
            username="admin_viewer", password="Password@123"
        )
        self.admin.groups.add(self.admin_group)

        self.staff_group, _ = Group.objects.get_or_create(name=STAFF)
        self.staff = get_user_model().objects.create_user(
            username="staff_viewer", password="Password@123"
        )
        self.staff.groups.add(self.staff_group)

        self.manager_group, _ = Group.objects.get_or_create(name=MANAGER)
        self.manager = get_user_model().objects.create_user(
            username="manager_viewer", password="Password@123"
        )
        self.manager.groups.add(self.manager_group)

        # Create multiple change logs
        self.log1 = ChangeLog.objects.create(
            component_id="HIST-01",
            component_name="Old Resistor",
            action="ADD",
            user=self.admin,
            details="Added initial batch",
        )
        self.log2 = ChangeLog.objects.create(
            component_id="HIST-02",
            component_name="Microcontroller IC",
            action="EDIT",
            user=self.admin,
            details="Stock increased to 50",
        )
        self.log3 = ChangeLog.objects.create(
            component_id="HIST-03",
            component_name="Obsolete Diode",
            action="DELETE",
            user=self.admin,
            details="Discontinued component",
        )

    def test_admin_can_view_change_history_page(self):
        """Story #58: Admin can view change history page listing all changes newest first."""
        self.client.force_login(self.admin)
        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "audit/log_list.html")
        self.assertTemplateUsed(response, "base.html")

        # Verify all changes are listed
        self.assertContains(response, "HIST-01")
        self.assertContains(response, "HIST-02")
        self.assertContains(response, "HIST-03")
        self.assertContains(response, "Added")
        self.assertContains(response, "Updated")
        self.assertContains(response, "Deactivated")

        # Verify newest first order
        logs_in_context = list(response.context["logs"])
        self.assertEqual(logs_in_context[0].component_id, "HIST-03")
        self.assertEqual(logs_in_context[1].component_id, "HIST-02")
        self.assertEqual(logs_in_context[2].component_id, "HIST-01")

    def test_filter_change_history_by_action(self):
        """Story #58: Filtering history by action returns matching records only."""
        self.client.force_login(self.admin)
        response = self.client.get(self.history_url, {"action": "DELETE"})
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "HIST-03")
        self.assertNotContains(response, "HIST-01")
        self.assertNotContains(response, "HIST-02")
        self.assertEqual(response.context["total_logs"], 1)

    def test_search_change_history_by_component_id(self):
        """Story #58: Searching history by ID or name filters properly."""
        self.client.force_login(self.admin)
        response = self.client.get(self.history_url, {"q": "HIST-02"})
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "HIST-02")
        self.assertNotContains(response, "HIST-01")
        self.assertNotContains(response, "HIST-03")

    def test_staff_and_manager_are_blocked_from_audit_history(self):
        """FR-14 / TC-SEC-01 / TC-SEC-02: Non-admin roles receive 403 Access Denied."""
        for user in [self.staff, self.manager]:
            with self.subTest(username=user.username):
                self.client.force_login(user)
                response = self.client.get(self.history_url)
                self.assertEqual(response.status_code, 403)
                self.assertContains(response, "Access denied", status_code=403)

    def test_unauthenticated_user_redirected_to_login(self):
        """Unauthenticated requests are redirected to login."""
        response = self.client.get(self.history_url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.history_url}")
