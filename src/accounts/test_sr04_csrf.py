"""
SR-04 security test (ESIM-SR-004, TC-SEC-04) – story #44.

Every form that changes data must carry a CSRF token, and requests without
a valid token must be rejected.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse

from accounts.roles import ADMIN
from inventory.models import Component


class CsrfProtectionTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(username="sec04", password="Sec@12345")
        self.admin.groups.add(Group.objects.get(name=ADMIN))
        self.component = Component.objects.create(
            component_id="SEC-004", name="CSRF Part", price="5.00", quantity=10, minimum_stock=2
        )
        # A client that behaves like a real browser: CSRF checks are switched on
        self.strict = Client(enforce_csrf_checks=True)

    def test_csrf_middleware_enabled(self):
        from django.conf import settings

        self.assertIn("django.middleware.csrf.CsrfViewMiddleware", settings.MIDDLEWARE)

    def test_forms_contain_csrf_token(self):
        self.strict.force_login(self.admin)
        pk = self.component.pk
        pages = [
            reverse("inventory:add"),
            reverse("inventory:edit", args=[pk]),
            reverse("inventory:delete", args=[pk]),
            reverse("inventory:list"),  # logout form in the header
        ]
        for url in pages:
            with self.subTest(url=url):
                self.assertContains(self.strict.get(url), "csrfmiddlewaretoken")
        self.strict.logout()
        self.assertContains(self.strict.get(reverse("accounts:login")), "csrfmiddlewaretoken")

    def test_login_without_token_is_rejected(self):
        get_user_model().objects.create_user(username="sec04b", password="Sec@12345")
        response = self.strict.post(
            reverse("accounts:login"), {"username": "sec04b", "password": "Sec@12345"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("_auth_user_id", self.strict.session)

    def test_add_without_token_is_rejected(self):
        self.strict.force_login(self.admin)
        data = {
            "component_id": "SEC-FAKE", "name": "Forged", "category": "Other", "description": "",
            "price": "1.00", "quantity": "1", "minimum_stock": "0", "is_active": "on",
        }
        response = self.strict.post(reverse("inventory:add"), data)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Component.objects.filter(component_id="SEC-FAKE").exists())

    def test_delete_without_token_is_rejected(self):
        self.strict.force_login(self.admin)
        response = self.strict.post(reverse("inventory:delete", args=[self.component.pk]))
        self.assertEqual(response.status_code, 403)
        self.component.refresh_from_db()
        self.assertTrue(self.component.is_active)

    def test_request_with_valid_token_works(self):
        self.strict.force_login(self.admin)
        page = self.strict.get(reverse("inventory:delete", args=[self.component.pk]))
        token = page.context["csrf_token"]
        response = self.strict.post(
            reverse("inventory:delete", args=[self.component.pk]), {"csrfmiddlewaretoken": str(token)}
        )
        self.assertEqual(response.status_code, 302)
