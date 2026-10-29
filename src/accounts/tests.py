from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LogoutSessionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="session-user",
            password="correct-horse-battery-staple",
        )

    def test_logout_ends_session_and_redirects_to_login(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_protected_page_requires_login_after_logout(self):
        self.client.force_login(self.user)
        profile_url = reverse("accounts:profile")
        self.assertEqual(self.client.get(profile_url).status_code, 200)

        self.client.post(reverse("accounts:logout"))
        response = self.client.get(profile_url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={profile_url}",
        )

    def test_protected_profile_is_not_cached(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("no-store", response["Cache-Control"])


class LoginTests(TestCase):
    """FR-01: users must log in with valid credentials (TC-AUTH-01)."""

    def setUp(self):
        self.login_url = reverse("accounts:login")
        get_user_model().objects.create_user(username="staff1", password="Store@123")

    def test_login_page_loads(self):
        """#34: login page has username, password and a Sign In button."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, "Sign In")

    def test_valid_login_opens_inventory(self):
        """#35: correct details log the user in and open the inventory list."""
        response = self.client.post(self.login_url, {"username": "staff1", "password": "Store@123"})
        self.assertRedirects(response, reverse("inventory:list"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_invalid_login_shows_error(self):
        """#35: wrong details are rejected with a clear message and no session."""
        response = self.client.post(self.login_url, {"username": "staff1", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_empty_fields_rejected(self):
        """#34: empty username/password does not log in."""
        response = self.client.post(self.login_url, {"username": "", "password": ""})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)


class ProtectedPageTests(TestCase):
    """#36: inventory pages cannot be opened without logging in (TC-SEC-01)."""

    PROTECTED = [
        ("inventory:list", []),
        ("inventory:add", []),
        ("inventory:edit", [1]),
        ("inventory:delete", [1]),
        ("inventory:low_stock", []),
        ("reports:dashboard", []),
        ("reports:report_list", []),
        ("audit:log_list", []),
        ("accounts:profile", []),
    ]

    def test_protected_pages_redirect_to_login(self):
        for name, args in self.PROTECTED:
            with self.subTest(page=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertRedirects(
                    response, f"{reverse('accounts:login')}?next={url}", fetch_redirect_response=False
                )

    def test_logged_in_user_can_open_inventory(self):
        user = get_user_model().objects.create_user(username="staff2", password="Store@123")
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("inventory:list")).status_code, 200)


class RoleAuthorizationTests(TestCase):
    """FR-14: each role can only do what it is allowed to (TC-SEC-01, TC-SEC-02)."""

    def setUp(self):
        from django.contrib.auth.models import Group

        from inventory.models import Component

        from .roles import ADMIN, MANAGER, STAFF

        self.users = {}
        for username, role in [("admin1", ADMIN), ("staff1", STAFF), ("manager1", MANAGER)]:
            user = get_user_model().objects.create_user(username=username, password="Demo@1234")
            user.groups.add(Group.objects.get(name=role))
            self.users[username] = user
        self.component = Component.objects.create(
            component_id="ROLE-001", name="Role Test Resistor", category="Passives",
            price="1.00", quantity=50, minimum_stock=10,
        )
        pk = self.component.pk
        self.restricted = [
            reverse("inventory:add"),
            reverse("inventory:edit", args=[pk]),
            reverse("inventory:delete", args=[pk]),
            reverse("audit:log_list"),
        ]

    def test_three_roles_exist(self):
        """#37: Admin, Staff and Manager groups are created automatically."""
        from django.contrib.auth.models import Group

        from .roles import ROLES

        self.assertEqual(
            set(Group.objects.filter(name__in=ROLES).values_list("name", flat=True)), set(ROLES)
        )

    def test_admin_has_full_permissions(self):
        """#37: the administrator can add, edit and delete components and manage users."""
        admin = self.users["admin1"]
        for perm in ["add_component", "change_component", "delete_component"]:
            self.assertTrue(admin.has_perm(f"inventory.{perm}"))
        self.assertTrue(admin.has_perm("auth.add_user"))
        self.assertFalse(self.users["staff1"].has_perm("inventory.add_component"))

    def test_admin_can_open_restricted_pages(self):
        """#38: the allowed role gets through."""
        self.client.force_login(self.users["admin1"])
        for url in self.restricted:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_staff_and_manager_are_blocked(self):
        """#38 / #39: Staff and Manager see the Access-denied page (403) for admin-only actions."""
        for username in ["staff1", "manager1"]:
            self.client.force_login(self.users[username])
            for url in self.restricted:
                with self.subTest(user=username, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, 403)
                    self.assertContains(response, "Access denied", status_code=403)

    def test_blocked_post_changes_nothing(self):
        """#38: a direct POST from Staff is refused on the server and the record is unchanged."""
        self.client.force_login(self.users["staff1"])
        pk = self.component.pk
        self.client.post(reverse("inventory:delete", args=[pk]))
        self.client.post(reverse("inventory:edit", args=[pk]), {"name": "Hacked"})
        self.component.refresh_from_db()
        self.assertTrue(self.component.is_active)
        self.assertEqual(self.component.name, "Role Test Resistor")

    def test_staff_and_manager_can_view_inventory(self):
        """Staff and Manager can still view the inventory list."""
        for username in ["staff1", "manager1"]:
            self.client.force_login(self.users[username])
            self.assertEqual(self.client.get(reverse("inventory:list")).status_code, 200)

    def test_role_shown_and_admin_links_hidden(self):
        """The header shows the role; admin-only links are hidden from other roles."""
        self.client.force_login(self.users["manager1"])
        response = self.client.get(reverse("inventory:list"))
        self.assertContains(response, "Store Manager")
        self.assertNotContains(response, reverse("audit:log_list"))
