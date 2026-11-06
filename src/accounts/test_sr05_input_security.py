"""
SR-05 security tests (ESIM-SR-005, TC-SEC-05) – stories #45 and #46.

#45: Harmful input (SQL injection, HTML/script) is rejected or made harmless.
#46: The server validates every value itself, even when browser checks are skipped.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from accounts.roles import ADMIN
from inventory.models import Component

SQL_INJECTIONS = [
    "' OR '1'='1",
    "'; DROP TABLE inventory_component; --",
    "1 UNION SELECT username, password FROM auth_user --",
]
SCRIPT = "<script>alert('x')</script>"


class HarmfulInputTests(TestCase):
    """Story #45"""

    def setUp(self):
        self.admin = get_user_model().objects.create_user(username="sec05", password="Sec@12345")
        self.admin.groups.add(Group.objects.get(name=ADMIN))
        self.client.force_login(self.admin)
        Component.objects.create(component_id="SEC-005", name="Safe Part", price="2.00", quantity=9, minimum_stock=1)

    def test_sql_injection_in_search_is_harmless(self):
        for text in SQL_INJECTIONS:
            with self.subTest(text=text):
                response = self.client.get(reverse("inventory:list"), {"q": text})
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, "pbkdf2_sha256")
        # The table still exists and still holds its data
        self.assertTrue(Component.objects.filter(component_id="SEC-005").exists())

    def test_sql_injection_cannot_bypass_login(self):
        self.client.logout()
        for text in SQL_INJECTIONS:
            with self.subTest(text=text):
                self.client.post(reverse("accounts:login"), {"username": text, "password": text})
                self.assertNotIn("_auth_user_id", self.client.session)

    def test_script_in_name_is_escaped_on_page(self):
        data = {
            "component_id": "SEC-XSS", "name": SCRIPT, "category": "Other", "description": SCRIPT,
            "price": "1.00", "quantity": "1", "minimum_stock": "0", "is_active": "on",
        }
        self.client.post(reverse("inventory:add"), data)
        response = self.client.get(reverse("inventory:list"))
        self.assertNotContains(response, SCRIPT)
        if Component.objects.filter(component_id="SEC-XSS").exists():
            self.assertContains(response, "&lt;script&gt;")

    def test_script_in_search_box_is_escaped(self):
        response = self.client.get(reverse("inventory:list"), {"q": SCRIPT})
        self.assertNotContains(response, SCRIPT)


class ServerSideValidationTests(TestCase):
    """Story #46: bad data sent directly (no browser checks) is still rejected."""

    def setUp(self):
        self.admin = get_user_model().objects.create_user(username="sec05b", password="Sec@12345")
        self.admin.groups.add(Group.objects.get(name=ADMIN))
        self.client.force_login(self.admin)

    def valid(self, **changes):
        data = {
            "component_id": "SEC-VAL", "name": "Valid Part", "category": "Other", "description": "",
            "price": "3.00", "quantity": "4", "minimum_stock": "1", "is_active": "on",
        }
        data.update(changes)
        return data

    def test_bad_values_are_rejected_and_not_saved(self):
        bad_inputs = [
            {"price": "-5"},
            {"price": "abc"},
            {"quantity": "-1"},
            {"quantity": "1.5"},
            {"minimum_stock": "-3"},
            {"component_id": ""},
            {"name": "   "},
            {"category": "NotACategory"},
            {"name": "x" * 5000},
        ]
        for change in bad_inputs:
            with self.subTest(change=list(change)[0]):
                response = self.client.post(reverse("inventory:add"), self.valid(**change))
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
                self.assertFalse(Component.objects.filter(component_id="SEC-VAL").exists())

    def test_duplicate_id_rejected(self):
        self.client.post(reverse("inventory:add"), self.valid())
        response = self.client.post(reverse("inventory:add"), self.valid(name="Second"))
        self.assertEqual(Component.objects.filter(component_id="SEC-VAL").count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_valid_data_is_saved(self):
        response = self.client.post(reverse("inventory:add"), self.valid())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Component.objects.filter(component_id="SEC-VAL").exists())
