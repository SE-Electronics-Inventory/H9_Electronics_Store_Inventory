"""FR-15 tests for friendly errors and operation feedback."""

from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import DatabaseError
from django.test import Client, TestCase, override_settings
from django.urls import path, reverse

from .forms import ComponentForm
from .models import Component


def _raise_test_server_error(request):
    raise RuntimeError("private database host and query details")


handler404 = "esims.views.page_not_found"
handler500 = "esims.views.server_error"
urlpatterns = [path("__fr15_test_server_error__/", _raise_test_server_error)]


class FriendlyErrorPageTests(TestCase):
    def test_production_urlconf_registers_custom_error_handlers(self):
        from esims import urls as project_urls

        self.assertEqual(project_urls.handler404, "esims.views.page_not_found")
        self.assertEqual(project_urls.handler500, "esims.views.server_error")

    @override_settings(DEBUG=False)
    def test_missing_component_uses_friendly_404_page(self):
        admin_group, _ = Group.objects.get_or_create(
            name="Inventory Administrator"
        )
        user = get_user_model().objects.create_user(
            username="error-page-viewer",
            password="test-password-123",
        )
        user.groups.add(admin_group)
        self.client.force_login(user)

        response = self.client.get(
            reverse("inventory:edit", args=[999999]),
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(response, "We couldn't find that page.", status_code=404)
        self.assertNotContains(response, "Traceback", status_code=404)

    def test_unexpected_server_error_uses_friendly_500_page(self):
        user = get_user_model().objects.create_user(
            username="server-error-viewer",
            password="test-password-123",
        )
        client = Client(raise_request_exception=False)
        client.force_login(user)

        with override_settings(DEBUG=False, ROOT_URLCONF=__name__):
            response = client.get(
                "/__fr15_test_server_error__/",
                HTTP_HOST="localhost",
            )

        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(response, "500.html")
        self.assertContains(response, "Something went wrong.", status_code=500)
        self.assertNotContains(response, "RuntimeError", status_code=500)
        self.assertNotContains(response, "private database host", status_code=500)


class OperationFeedbackTests(TestCase):
    def setUp(self):
        admin_group, _ = Group.objects.get_or_create(name="Inventory Administrator")
        self.admin = get_user_model().objects.create_user(
            username="feedback-admin",
            password="test-password-123",
        )
        self.admin.groups.add(admin_group)
        self.client.force_login(self.admin)

    def valid_data(self, **overrides):
        data = {
            "component_id": "FEEDBACK-001",
            "name": "Feedback Sensor",
            "category": "Sensors",
            "description": "Component for feedback tests",
            "price": "12.50",
            "quantity": "8",
            "minimum_stock": "3",
            "is_active": "on",
        }
        data.update(overrides)
        return data

    def create_component(self, component_id="FEEDBACK-001"):
        return Component.objects.create(
            component_id=component_id,
            name="Existing Sensor",
            price=Decimal("10.00"),
            quantity=5,
            minimum_stock=3,
        )

    def test_add_edit_and_deactivate_show_success_messages(self):
        add_response = self.client.post(
            reverse("inventory:add"), self.valid_data(), follow=True
        )
        self.assertContains(add_response, "Component added successfully.")

        component = Component.objects.get(component_id="FEEDBACK-001")
        edit_response = self.client.post(
            reverse("inventory:edit", args=[component.pk]),
            self.valid_data(name="Updated Sensor"),
            follow=True,
        )
        self.assertContains(edit_response, "Component updated successfully.")

        delete_response = self.client.post(
            reverse("inventory:delete", args=[component.pk]),
            follow=True,
        )
        self.assertContains(delete_response, "Component deactivated successfully.")
        component.refresh_from_db()
        self.assertFalse(component.is_active)

    def test_invalid_add_shows_friendly_error_and_saves_nothing(self):
        response = self.client.post(
            reverse("inventory:add"),
            self.valid_data(name="", quantity="-1"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The component could not be saved.")
        self.assertContains(response, "Please correct the highlighted fields.")
        self.assertNotContains(response, "Traceback")
        self.assertFalse(Component.objects.exists())

    def test_duplicate_add_shows_friendly_error_without_changing_existing_record(self):
        existing = self.create_component()

        response = self.client.post(reverse("inventory:add"), self.valid_data())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The component could not be saved.")
        self.assertContains(response, "already exists")
        self.assertEqual(Component.objects.count(), 1)
        existing.refresh_from_db()
        self.assertEqual(existing.name, "Existing Sensor")

    def test_invalid_edit_shows_friendly_error_and_preserves_existing_record(self):
        component = self.create_component()

        response = self.client.post(
            reverse("inventory:edit", args=[component.pk]),
            self.valid_data(component_id="", name="", price="-1", quantity="-2"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The component could not be saved.")
        self.assertContains(response, "Please correct the highlighted fields.")
        component.refresh_from_db()
        self.assertEqual(component.component_id, "FEEDBACK-001")
        self.assertEqual(component.name, "Existing Sensor")
        self.assertEqual(component.price, Decimal("10.00"))
        self.assertEqual(component.quantity, 5)

    def test_database_failure_during_add_is_generic_and_persists_nothing(self):
        with patch.object(
            ComponentForm,
            "save",
            side_effect=DatabaseError("private database connection detail"),
        ):
            response = self.client.post(
                reverse("inventory:add"), self.valid_data()
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No changes were made.")
        self.assertNotContains(response, "private database connection detail")
        self.assertFalse(Component.objects.exists())

    def test_database_failure_during_deactivation_preserves_component(self):
        component = self.create_component()

        with patch.object(
            Component,
            "save",
            side_effect=DatabaseError("private database connection detail"),
        ):
            response = self.client.post(
                reverse("inventory:delete", args=[component.pk]),
                follow=True,
            )

        self.assertContains(response, "The component could not be deactivated.")
        self.assertContains(response, "No changes were made.")
        self.assertNotContains(response, "private database connection detail")
        component.refresh_from_db()
        self.assertTrue(component.is_active)
