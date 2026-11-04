"""
Tests for Transaction Reliability (NFR-03: ESIM-NF-003 / TC-REL-01)
Covers User Story #59 (save changes in database transactions)
and User Story #60 (test that a failed save changes nothing).
"""
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from accounts.roles import ADMIN
from audit.models import ChangeLog
from inventory.models import Component


class TransactionReliabilityTests(TestCase):
    """
    Test suite for ESIM-NF-003 / TC-REL-01:
    A valid inventory transaction shall either complete successfully or leave the
    affected record in its previous valid state.
    """

    def setUp(self):
        self.client = Client()
        self.admin_group, _ = Group.objects.get_or_create(name=ADMIN)
        self.admin = get_user_model().objects.create_user(
            username="admin_txn", password="Password@123"
        )
        self.admin.groups.add(self.admin_group)
        self.client.force_login(self.admin)

    # -------------------------------------------------------------------------
    # Component Addition Transaction Tests (Story #59 & Story #60)
    # -------------------------------------------------------------------------
    def test_successful_add_commits_atomically(self):
        """
        Story #59: Valid addition runs inside a transaction and commits all changes.
        """
        data = {
            "component_id": "TXN-ADD-001",
            "name": "Transaction Resistor",
            "category": "Passives",
            "description": "100k Ohm resistor",
            "price": "5.50",
            "quantity": "100",
            "minimum_stock": "20",
        }
        response = self.client.post(reverse("inventory:add"), data)
        self.assertRedirects(response, reverse("inventory:list"))

        # Component and audit log both exist in DB
        comp = Component.objects.get(component_id="TXN-ADD-001")
        self.assertEqual(comp.name, "Transaction Resistor")
        self.assertTrue(ChangeLog.objects.filter(component_id="TXN-ADD-001", action="ADD").exists())

    def test_failed_add_rolls_back_completely(self):
        """
        Story #60 / TC-REL-01: When an error is forced after initial save during addition,
        the transaction rolls back completely and no orphan records are persisted.
        """
        data = {
            "component_id": "TXN-FAIL-001",
            "name": "Failed Add Sensor",
            "category": "Sensors",
            "description": "Temperature sensor",
            "price": "90.00",
            "quantity": "15",
            "minimum_stock": "5",
        }

        # Force a failure during the audit log write inside the atomic block
        with patch("inventory.views.log_change", side_effect=RuntimeError("Simulated DB connection failure")):
            response = self.client.post(reverse("inventory:add"), data)

        # Database must roll back: component is NOT saved
        self.assertFalse(Component.objects.filter(component_id="TXN-FAIL-001").exists())
        self.assertFalse(ChangeLog.objects.filter(component_id="TXN-FAIL-001").exists())

    # -------------------------------------------------------------------------
    # Component Update Transaction Tests (Story #59 & Story #60)
    # -------------------------------------------------------------------------
    def test_successful_edit_commits_atomically(self):
        """
        Story #59: Valid edit runs inside a transaction and commits all changes.
        """
        comp = Component.objects.create(
            component_id="TXN-EDIT-001",
            name="Original IC Name",
            category="Semiconductors",
            price=Decimal("45.00"),
            quantity=30,
            minimum_stock=10,
        )

        data = {
            "component_id": "TXN-EDIT-001",
            "name": "Updated IC Name",
            "category": "Semiconductors",
            "description": "Updated description",
            "price": "55.00",
            "quantity": "40",
            "minimum_stock": "10",
        }
        response = self.client.post(reverse("inventory:edit", args=[comp.pk]), data)
        self.assertRedirects(response, reverse("inventory:list"))

        comp.refresh_from_db()
        self.assertEqual(comp.name, "Updated IC Name")
        self.assertEqual(comp.price, Decimal("55.00"))
        self.assertEqual(comp.quantity, 40)
        self.assertTrue(ChangeLog.objects.filter(component_id="TXN-EDIT-001", action="EDIT").exists())

    def test_failed_edit_leaves_record_in_previous_valid_state(self):
        """
        Story #60 / TC-REL-01: When an update fails mid-transaction, the transaction rolls back
        and the component record remains exactly in its previous valid state.
        """
        comp = Component.objects.create(
            component_id="TXN-FAIL-EDIT",
            name="Stable Component Name",
            category="Passives",
            price=Decimal("12.00"),
            quantity=50,
            minimum_stock=10,
        )

        data = {
            "component_id": "TXN-FAIL-EDIT",
            "name": "Corrupted New Name",
            "category": "Passives",
            "description": "Corrupted description",
            "price": "99.99",
            "quantity": "999",
            "minimum_stock": "10",
        }

        # Force a failure inside the atomic block after model write
        with patch("inventory.views.log_change", side_effect=RuntimeError("Simulated network glitch during logging")):
            response = self.client.post(reverse("inventory:edit", args=[comp.pk]), data)

        # The record MUST be in its previous valid state (TC-REL-01)
        comp.refresh_from_db()
        self.assertEqual(comp.name, "Stable Component Name")
        self.assertEqual(comp.price, Decimal("12.00"))
        self.assertEqual(comp.quantity, 50)
        # Ensure no change log was committed
        self.assertFalse(ChangeLog.objects.filter(component_id="TXN-FAIL-EDIT", action="EDIT").exists())

    # -------------------------------------------------------------------------
    # Component Deactivation Transaction Tests (Story #59 & Story #60)
    # -------------------------------------------------------------------------
    def test_successful_delete_commits_atomically(self):
        """
        Story #59: Deactivation runs inside a transaction and commits cleanly.
        """
        comp = Component.objects.create(
            component_id="TXN-DEL-001",
            name="Deletable Component",
            category="Other",
            price=Decimal("20.00"),
            quantity=10,
            minimum_stock=2,
            is_active=True,
        )

        response = self.client.post(reverse("inventory:delete", args=[comp.pk]))
        self.assertRedirects(response, reverse("inventory:list"))

        comp.refresh_from_db()
        self.assertFalse(comp.is_active)
        self.assertTrue(ChangeLog.objects.filter(component_id="TXN-DEL-001", action="DELETE").exists())

    def test_failed_delete_leaves_record_in_previous_valid_state(self):
        """
        Story #60 / TC-REL-01: When deactivation fails mid-transaction,
        the component remains active and unchanged.
        """
        comp = Component.objects.create(
            component_id="TXN-FAIL-DEL",
            name="Protected Active Component",
            category="Other",
            price=Decimal("35.00"),
            quantity=8,
            minimum_stock=2,
            is_active=True,
        )

        # Force a failure during the atomic delete transaction
        with patch("inventory.views.log_change", side_effect=RuntimeError("Simulated failure during deletion")):
            response = self.client.post(reverse("inventory:delete", args=[comp.pk]))

        # The record MUST remain in its previous valid state (is_active=True)
        comp.refresh_from_db()
        self.assertTrue(comp.is_active)
        self.assertFalse(ChangeLog.objects.filter(component_id="TXN-FAIL-DEL", action="DELETE").exists())
