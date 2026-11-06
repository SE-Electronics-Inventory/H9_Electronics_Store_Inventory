"""NFR-02 coverage for inventory behavior with 1,000 component records."""

from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from inventory.models import Component


class SeedComponentsCommandTests(TestCase):
    def test_default_seed_keeps_the_realistic_demo_dataset(self):
        call_command("seed_components", stdout=StringIO())
        self.assertEqual(Component.objects.count(), 11)
        self.assertTrue(Component.objects.filter(component_id="ESP32-WROOM").exists())

    def test_seed_command_creates_dataset_and_is_idempotent(self):
        call_command("seed_components", count=1000, stdout=StringIO())
        self.assertEqual(
            Component.objects.filter(component_id__startswith="SCALE-").count(), 1000
        )

        call_command("seed_components", count=1000, stdout=StringIO())
        self.assertEqual(
            Component.objects.filter(component_id__startswith="SCALE-").count(), 1000
        )


class InventoryScalabilityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Component.objects.bulk_create(
            [
                Component(
                    component_id=f"SCALE-{index:06d}",
                    name=f"Scalability Component {index:06d}",
                    category="Sensors",
                    description="Generated inventory record for NFR-02.",
                    price=Decimal("10.00"),
                    quantity=20,
                    minimum_stock=5,
                )
                for index in range(1, 1001)
            ],
            batch_size=250,
        )
        admin_group, _ = Group.objects.get_or_create(name="Inventory Administrator")
        cls.admin = get_user_model().objects.create_user(
            username="scalability-admin", password="scalability-test-password"
        )
        cls.admin.groups.add(admin_group)

    def setUp(self):
        self.client.force_login(self.admin)

    def test_list_search_add_edit_and_deactivate_work_with_1000_records(self):
        response = self.client.get(reverse("inventory:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["components"].count(), 1000)

        response = self.client.get(reverse("inventory:list"), {"q": "SCALE-001000"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["components"].count(), 1)
        self.assertContains(response, "Scalability Component 001000")

        data = {
            "component_id": "SCALE-CRUD-001",
            "name": "CRUD check at scale",
            "category": "Microcontrollers",
            "description": "Created while validating NFR-02.",
            "price": "250.00",
            "quantity": "8",
            "minimum_stock": "3",
            "is_active": "on",
        }
        response = self.client.post(reverse("inventory:add"), data)
        self.assertEqual(response.status_code, 302)
        component = Component.objects.get(component_id="SCALE-CRUD-001")

        data.update({"quantity": "18", "name": "CRUD check updated at scale"})
        response = self.client.post(reverse("inventory:edit", args=[component.pk]), data)
        self.assertEqual(response.status_code, 302)
        component.refresh_from_db()
        self.assertEqual(component.quantity, 18)
        self.assertEqual(component.name, "CRUD check updated at scale")

        response = self.client.post(reverse("inventory:delete", args=[component.pk]))
        self.assertEqual(response.status_code, 302)
        component.refresh_from_db()
        self.assertFalse(component.is_active)
