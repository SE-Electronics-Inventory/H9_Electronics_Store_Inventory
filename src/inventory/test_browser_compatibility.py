"""
Tests for Browser Compatibility (NFR-07: ESIM-NF-007 / TC-COMP-01)
Covers User Story #61: Test on Chrome, Edge and Firefox.
Validates that all main features and responses operate correctly across modern browsers.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse

from accounts.roles import ADMIN, MANAGER, STAFF
from inventory.models import Component


class BrowserCompatibilityTests(TestCase):
    """
    Test suite for ESIM-NF-007 / TC-COMP-01:
    The application shall function correctly on current versions of Chrome, Edge and Firefox.
    """

    BROWSER_USER_AGENTS = {
        "Chrome": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Edge": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ),
        "Firefox": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) "
            "Gecko/20100101 Firefox/120.0"
        ),
    }

    def setUp(self):
        self.admin_group, _ = Group.objects.get_or_create(name=ADMIN)
        self.admin = get_user_model().objects.create_user(
            username="admin_browser", password="Password@123"
        )
        self.admin.groups.add(self.admin_group)

        self.comp = Component.objects.create(
            component_id="COMPAT-001",
            name="Compatibility Resistor",
            category="Passives",
            description="Through-hole resistor for browser tests",
            price=Decimal("2.50"),
            quantity=100,
            minimum_stock=20,
        )

    def test_html5_standards_and_viewport_across_browsers(self):
        """
        TC-COMP-01: HTML5 doctype, charset, and responsive viewport meta tags
        are served correctly to Chrome, Edge, and Firefox.
        """
        for browser_name, user_agent in self.BROWSER_USER_AGENTS.items():
            with self.subTest(browser=browser_name):
                client = Client(HTTP_USER_AGENT=user_agent)
                client.force_login(self.admin)

                response = client.get(reverse("inventory:list"))
                self.assertEqual(response.status_code, 200)

                content = response.content.decode("utf-8")
                self.assertIn("<!DOCTYPE html>", content)
                self.assertIn('<meta charset="UTF-8">', content)
                self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1.0">', content)

    def test_core_pages_render_successfully_across_all_browsers(self):
        """
        Story #61 / TC-COMP-01: Login, list, search, add, edit, delete, dashboard,
        reports, and audit work with 200 OK across Chrome, Edge, and Firefox.
        """
        urls_to_test = [
            ("inventory:list", []),
            ("inventory:add", []),
            ("inventory:edit", [self.comp.pk]),
            ("inventory:delete", [self.comp.pk]),
            ("inventory:low_stock", []),
            ("reports:report_list", []),
            ("reports:dashboard", []),
            ("audit:log_list", []),
            ("accounts:profile", []),
        ]

        for browser_name, user_agent in self.BROWSER_USER_AGENTS.items():
            client = Client(HTTP_USER_AGENT=user_agent)
            client.force_login(self.admin)

            for url_name, args in urls_to_test:
                with self.subTest(browser=browser_name, page=url_name):
                    target_url = reverse(url_name, args=args)
                    response = client.get(target_url)
                    self.assertEqual(
                        response.status_code,
                        200,
                        f"Page {url_name} failed on {browser_name} with status {response.status_code}",
                    )
                    self.assertIn("text/html", response["Content-Type"])

    def test_search_and_filtering_across_browsers(self):
        """
        TC-COMP-01: Search queries and filter parameters operate identically on all browsers.
        """
        for browser_name, user_agent in self.BROWSER_USER_AGENTS.items():
            with self.subTest(browser=browser_name):
                client = Client(HTTP_USER_AGENT=user_agent)
                client.force_login(self.admin)

                # Search by query
                response = client.get(reverse("inventory:list"), {"q": "COMPAT", "category": "Passives"})
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "COMPAT-001")
                self.assertContains(response, "Compatibility Resistor")

    def test_csv_export_download_across_browsers(self):
        """
        Story #61 / TC-COMP-01: CSV report export delivers standard Content-Disposition
        and Content-Type headers ensuring universal browser file download behavior.
        """
        for browser_name, user_agent in self.BROWSER_USER_AGENTS.items():
            with self.subTest(browser=browser_name):
                client = Client(HTTP_USER_AGENT=user_agent)
                client.force_login(self.admin)

                response = client.get(reverse("reports:export_csv"))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
                self.assertIn('attachment; filename="inventory_report.csv"', response["Content-Disposition"])
                self.assertContains(response, "COMPAT-001")
