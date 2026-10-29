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
