"""Measure inventory list, search, and CRUD response time under normal load."""

import json
import math
from time import perf_counter

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from inventory.models import Component


class InventoryResponsePerformanceTests(TestCase):
    """TC-PERF-01: at least 90% of normal-load requests finish within 2 seconds."""

    iterations = 10
    threshold_ms = 2000

    @classmethod
    def setUpTestData(cls):
        admin_group, _ = Group.objects.get_or_create(name="Inventory Administrator")
        cls.admin = get_user_model().objects.create_user(
            username="performance-admin", password="performance-test-password"
        )
        cls.admin.groups.add(admin_group)

    def setUp(self):
        self.client.force_login(self.admin)
        self.timings = {name: [] for name in ("list", "search", "add", "edit", "delete")}

    def _measure(self, name, request, expected_status):
        start = perf_counter()
        response = request()
        elapsed_ms = (perf_counter() - start) * 1000
        self.assertEqual(response.status_code, expected_status)
        self.timings[name].append(elapsed_ms)
        return response

    @staticmethod
    def _component_data(component_id, **overrides):
        data = {
            "component_id": component_id,
            "name": f"Benchmark component {component_id}",
            "category": "Sensors",
            "description": "Temporary record for TC-PERF-01",
            "price": "125.50",
            "quantity": "20",
            "minimum_stock": "5",
            "is_active": "on",
        }
        data.update(overrides)
        return data

    def test_list_search_add_edit_and_delete_meet_response_target(self):
        for index in range(self.iterations):
            component_id = f"PERF-{index:03d}"
            self._measure(
                "list",
                lambda: self.client.get(reverse("inventory:list")),
                200,
            )
            self._measure(
                "search",
                lambda: self.client.get(
                    reverse("inventory:list"), {"q": component_id}
                ),
                200,
            )
            self._measure(
                "add",
                lambda: self.client.post(
                    reverse("inventory:add"), self._component_data(component_id)
                ),
                302,
            )
            component = Component.objects.get(component_id=component_id)
            self._measure(
                "edit",
                lambda: self.client.post(
                    reverse("inventory:edit", args=[component.pk]),
                    self._component_data(component_id, quantity="25"),
                ),
                302,
            )
            self._measure(
                "delete",
                lambda: self.client.post(
                    reverse("inventory:delete", args=[component.pk])
                ),
                302,
            )

        all_timings = [duration for values in self.timings.values() for duration in values]
        ordered = sorted(all_timings)
        p90_ms = ordered[math.ceil(0.90 * len(ordered)) - 1]
        within_target = sum(duration < self.threshold_ms for duration in all_timings)
        summary = {
            "test": "TC-PERF-01",
            "measurement": "Django test-client request time, including view, ORM, and template work",
            "threshold_ms": self.threshold_ms,
            "requests": len(all_timings),
            "within_threshold": within_target,
            "within_threshold_percent": round(100 * within_target / len(all_timings), 2),
            "p90_ms": round(p90_ms, 2),
            "per_operation_p90_ms": {
                name: round(sorted(values)[math.ceil(0.90 * len(values)) - 1], 2)
                for name, values in self.timings.items()
            },
        }
        print("NFR01_PERFORMANCE=" + json.dumps(summary, sort_keys=True))
        self.assertGreaterEqual(within_target / len(all_timings), 0.90, summary)
