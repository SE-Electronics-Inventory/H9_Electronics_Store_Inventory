"""
Tests for Inventory Reports & CSV Export (FR-11: ESIM-F-011 / TC-REP-01)
Covers User Story #54 (generate report), User Story #55 (filter report),
and User Story #56 (export report as CSV).
"""
import csv
import io
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse

from accounts.roles import ADMIN, MANAGER, STAFF
from inventory.models import Component


class InventoryReportTests(TestCase):
    """
    Test suite for FR-11: Generate Inventory Reports (ESIM-F-011 / TC-REP-01).
    """

    def setUp(self):
        self.client = Client()
        self.report_url = reverse("reports:report_list")
        self.export_url = reverse("reports:export_csv")

        # Create user accounts for testing
        self.manager_group, _ = Group.objects.get_or_create(name=MANAGER)
        self.manager = get_user_model().objects.create_user(
            username="manager_test", password="Password@123"
        )
        self.manager.groups.add(self.manager_group)

        self.admin_group, _ = Group.objects.get_or_create(name=ADMIN)
        self.admin = get_user_model().objects.create_user(
            username="admin_test", password="Password@123"
        )
        self.admin.groups.add(self.admin_group)

        # Create test inventory components (TC-REP-01 dataset)
        # In stock component (qty > min_stock)
        self.c1 = Component.objects.create(
            component_id="REP-ESP32",
            name="ESP32 Development Board",
            category="Microcontrollers",
            description="Dual core 240MHz microcontroller",
            price=Decimal("450.00"),
            quantity=25,
            minimum_stock=10,
            is_active=True,
        )
        # Low stock component (0 < qty <= min_stock)
        self.c2 = Component.objects.create(
            component_id="REP-DHT11",
            name="DHT11 Temp Sensor Module",
            category="Sensors",
            description="Digital temperature sensor",
            price=Decimal("95.50"),
            quantity=4,
            minimum_stock=8,
            is_active=True,
        )
        # Out of stock component (qty = 0)
        self.c3 = Component.objects.create(
            component_id="REP-L298N",
            name="L298N Motor Driver",
            category="Semiconductors",
            description="Dual H-bridge driver module",
            price=Decimal("160.00"),
            quantity=0,
            minimum_stock=5,
            is_active=True,
        )
        # Inactive / deactivated component (should be excluded from report)
        self.c_inactive = Component.objects.create(
            component_id="REP-DEACT",
            name="Old Deactivated Chip",
            category="Semiconductors",
            price=Decimal("50.00"),
            quantity=10,
            minimum_stock=5,
            is_active=False,
        )

    # -------------------------------------------------------------
    # Story #54: Generate inventory report
    # -------------------------------------------------------------
    def test_unauthenticated_user_redirected_to_login(self):
        """Unauthenticated requests to reports and export must redirect to login."""
        for url in [self.report_url, self.export_url]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")

    def test_store_manager_can_generate_inventory_report(self):
        """
        Story #54 / TC-REP-01: Store Manager can access report page and view all active components
        with their stored details, quantity, and availability status.
        """
        self.client.force_login(self.manager)
        response = self.client.get(self.report_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reports/report_list.html")
        self.assertTemplateUsed(response, "base.html")

        # Verify component records are displayed with details matching DB
        self.assertContains(response, "REP-ESP32")
        self.assertContains(response, "ESP32 Development Board")
        self.assertContains(response, "450.00")
        self.assertContains(response, "25")
        self.assertContains(response, "In Stock")

        self.assertContains(response, "REP-DHT11")
        self.assertContains(response, "DHT11 Temp Sensor Module")
        self.assertContains(response, "95.50")
        self.assertContains(response, "4")
        self.assertContains(response, "Low Stock")

        self.assertContains(response, "REP-L298N")
        self.assertContains(response, "Out of Stock")

        # Deactivated items should not appear in active inventory report
        self.assertNotContains(response, "REP-DEACT")

    def test_inventory_report_summary_calculations(self):
        """
        Story #54: Report accurately calculates total items, total units, valuation and availability counts.
        """
        self.client.force_login(self.manager)
        response = self.client.get(self.report_url)
        self.assertEqual(response.status_code, 200)

        # 3 active items total
        self.assertEqual(response.context["total_items"], 3)
        # 25 + 4 + 0 = 29 total units
        self.assertEqual(response.context["total_units"], 29)
        # (25 * 450) + (4 * 95.50) + (0 * 160) = 11250 + 382 = 11632.00
        expected_val = (25 * Decimal("450.00")) + (4 * Decimal("95.50"))
        self.assertEqual(response.context["total_value"], expected_val)
        self.assertEqual(response.context["in_stock_count"], 1)
        self.assertEqual(response.context["low_stock_count"], 1)
        self.assertEqual(response.context["out_of_stock_count"], 1)

    # -------------------------------------------------------------
    # Story #55: Filter the report
    # -------------------------------------------------------------
    def test_filter_report_by_category(self):
        """
        Story #55: Choosing a category filter shows only components belonging to that category.
        """
        self.client.force_login(self.manager)
        response = self.client.get(self.report_url, {"category": "Sensors"})
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "REP-DHT11")
        self.assertNotContains(response, "REP-ESP32")
        self.assertNotContains(response, "REP-L298N")
        self.assertEqual(response.context["total_items"], 1)

    def test_filter_report_by_availability_low_stock(self):
        """
        Story #55: Filtering by 'Low Stock' shows only low stock items.
        """
        self.client.force_login(self.manager)
        response = self.client.get(self.report_url, {"availability": "Low Stock"})
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "REP-DHT11")
        self.assertNotContains(response, "REP-ESP32")
        self.assertNotContains(response, "REP-L298N")
        self.assertEqual(response.context["total_items"], 1)

    def test_filter_report_by_availability_out_of_stock(self):
        """
        Story #55: Filtering by 'Out of Stock' shows only out of stock items.
        """
        self.client.force_login(self.manager)
        response = self.client.get(self.report_url, {"availability": "Out of Stock"})
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "REP-L298N")
        self.assertNotContains(response, "REP-ESP32")
        self.assertNotContains(response, "REP-DHT11")
        self.assertEqual(response.context["total_items"], 1)

    def test_filter_report_by_category_and_availability_combined(self):
        """
        Story #55: Combining category and availability filters works correctly.
        """
        self.client.force_login(self.manager)
        # Microcontrollers + In Stock -> REP-ESP32
        response = self.client.get(
            self.report_url, {"category": "Microcontrollers", "availability": "In Stock"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "REP-ESP32")
        self.assertNotContains(response, "REP-DHT11")
        self.assertEqual(response.context["total_items"], 1)

        # Microcontrollers + Out of Stock -> Empty
        response_empty = self.client.get(
            self.report_url, {"category": "Microcontrollers", "availability": "Out of Stock"}
        )
        self.assertEqual(response_empty.status_code, 200)
        self.assertContains(response_empty, "No components found for this report")
        self.assertEqual(response_empty.context["total_items"], 0)

    # -------------------------------------------------------------
    # Story #56: Export report as CSV
    # -------------------------------------------------------------
    def test_export_report_as_csv_headers_and_data(self):
        """
        Story #56: Downloading CSV provides a valid CSV file with all required headers and rows.
        """
        self.client.force_login(self.manager)
        response = self.client.get(self.export_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn('attachment; filename="inventory_report.csv"', response["Content-Disposition"])

        content = response.content.decode("utf-8")
        reader = list(csv.reader(io.StringIO(content)))

        # Verify Header Row
        expected_header = [
            "Component ID",
            "Component Name",
            "Category",
            "Unit Price (INR)",
            "Quantity in Stock",
            "Minimum Stock",
            "Availability Status",
        ]
        self.assertEqual(reader[0], expected_header)

        # Verify Row Count (header + 3 active components)
        self.assertEqual(len(reader), 4)

        # Check row contents
        rows_by_id = {row[0]: row for row in reader[1:]}
        self.assertIn("REP-ESP32", rows_by_id)
        self.assertEqual(rows_by_id["REP-ESP32"][1], "ESP32 Development Board")
        self.assertEqual(rows_by_id["REP-ESP32"][3], "450.00")
        self.assertEqual(rows_by_id["REP-ESP32"][4], "25")
        self.assertEqual(rows_by_id["REP-ESP32"][6], "In Stock")

        self.assertIn("REP-DHT11", rows_by_id)
        self.assertEqual(rows_by_id["REP-DHT11"][6], "Low Stock")

        self.assertIn("REP-L298N", rows_by_id)
        self.assertEqual(rows_by_id["REP-L298N"][6], "Out of Stock")

    def test_export_report_csv_with_filters(self):
        """
        Story #56: CSV export respects active filters so the download matches what is on screen.
        """
        self.client.force_login(self.manager)
        response = self.client.get(self.export_url, {"category": "Sensors"})
        self.assertEqual(response.status_code, 200)

        content = response.content.decode("utf-8")
        reader = list(csv.reader(io.StringIO(content)))

        # Header + 1 sensor item (REP-DHT11)
        self.assertEqual(len(reader), 2)
        self.assertEqual(reader[1][0], "REP-DHT11")

    def test_report_list_format_csv_parameter_triggers_export(self):
        """
        Story #56: Accessing report list with ?format=csv also returns the CSV export.
        """
        self.client.force_login(self.manager)
        response = self.client.get(self.report_url, {"format": "csv"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
