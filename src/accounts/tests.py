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
