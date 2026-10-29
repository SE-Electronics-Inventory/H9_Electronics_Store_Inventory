"""
SR-02 security tests (ESIM-SR-002, TC-SEC-02) – stories #41 and #42.

#41: Staff and Manager users are blocked from every admin-only action.
#42: Sending the request directly (not through the page buttons) is blocked too,
     and nothing in the database changes.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from accounts.roles import ADMIN, MANAGER, STAFF
from inventory.models import Component


class RoleEscalationTests(TestCase):
    def setUp(self):
        self.users = {}
        for username, role in [("admin-sec", ADMIN), ("staff-sec", STAFF), ("manager-sec", MANAGER)]:
            user = get_user_model().objects.create_user(username=username, password="Sec@12345")
            user.groups.add(Group.objects.get(name=role))
            self.users[role] = user
        self.no_role = get_user_model().objects.create_user(username="norole-sec", password="Sec@12345")
        self.component = Component.objects.create(
            component_id="SEC-002", name="Original Name", price="10.00", quantity=20, minimum_stock=5
        )
        pk = self.component.pk
        self.admin_pages = [
            reverse("inventory:add"),
            reverse("inventory:edit", args=[pk]),
            reverse("inventory:delete", args=[pk]),
            reverse("audit:log_list"),
        ]
        self.valid_new = {
            "component_id": "SEC-NEW", "name": "Injected Part", "category": "Other",
            "description": "", "price": "1.00", "quantity": "1", "minimum_stock": "0", "is_active": "on",
        }

    def blocked_users(self):
        return [self.users[STAFF], self.users[MANAGER], self.no_role]

    # Story #41
    def test_non_admin_roles_cannot_open_admin_pages(self):
        for user in self.blocked_users():
            self.client.force_login(user)
            for url in self.admin_pages:
                with self.subTest(user=user.username, url=url):
                    self.assertEqual(self.client.get(url).status_code, 403)

    def test_non_admin_roles_cannot_use_django_admin(self):
        for user in self.blocked_users():
            self.client.force_login(user)
            with self.subTest(user=user.username):
                response = self.client.get("/admin/auth/user/")
                self.assertNotEqual(response.status_code, 200)

    def test_admin_is_allowed(self):
        self.client.force_login(self.users[ADMIN])
        for url in self.admin_pages:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    # Story #42
    def test_direct_add_request_is_rejected(self):
        for user in self.blocked_users():
            self.client.force_login(user)
            with self.subTest(user=user.username):
                response = self.client.post(reverse("inventory:add"), self.valid_new)
                self.assertEqual(response.status_code, 403)
        self.assertFalse(Component.objects.filter(component_id="SEC-NEW").exists())

    def test_direct_edit_and_delete_requests_change_nothing(self):
        pk = self.component.pk
        for user in self.blocked_users():
            self.client.force_login(user)
            with self.subTest(user=user.username):
                edit = self.client.post(
                    reverse("inventory:edit", args=[pk]),
                    {**self.valid_new, "component_id": "SEC-002", "name": "Hacked"},
                )
                delete = self.client.post(reverse("inventory:delete", args=[pk]))
                self.assertEqual(edit.status_code, 403)
                self.assertEqual(delete.status_code, 403)
        self.component.refresh_from_db()
        self.assertEqual(self.component.name, "Original Name")
        self.assertTrue(self.component.is_active)

    def test_logged_out_direct_post_is_rejected(self):
        response = self.client.post(reverse("inventory:add"), self.valid_new)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Component.objects.filter(component_id="SEC-NEW").exists())
