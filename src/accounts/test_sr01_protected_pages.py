"""
SR-01 security test (ESIM-SR-001, TC-SEC-01) – story #40.

Every page of the application (except the login page) must require login.
The list of pages is read from the project's URL configuration, so any page
added later is checked automatically.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import URLPattern, URLResolver, get_resolver, reverse

PUBLIC_PAGES = {"accounts:login"}
SKIP_NAMESPACES = {"admin"}  # Django admin has its own staff login


def iter_named_urls(patterns, namespace=None):
    for pattern in patterns:
        if isinstance(pattern, URLResolver):
            ns = pattern.namespace or namespace
            if ns in SKIP_NAMESPACES:
                continue
            yield from iter_named_urls(pattern.url_patterns, ns)
        elif isinstance(pattern, URLPattern) and pattern.name:
            yield f"{namespace}:{pattern.name}" if namespace else pattern.name


def build_url(name):
    for args in ([], [1]):
        try:
            return reverse(name, args=args)
        except Exception:
            continue
    return None


class ProtectedPageSecurityTests(TestCase):
    def setUp(self):
        self.login_url = reverse("accounts:login")
        self.pages = sorted(
            n for n in set(iter_named_urls(get_resolver().url_patterns)) if n not in PUBLIC_PAGES
        )

    def test_url_list_is_not_empty(self):
        self.assertGreater(len(self.pages), 5)

    def test_every_protected_page_redirects_to_login(self):
        """Opening any page without logging in sends the user to the login page."""
        for name in self.pages:
            url = build_url(name)
            if url is None:
                continue
            with self.subTest(page=name, url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response["Location"].startswith(self.login_url))

    def test_no_inventory_data_shown_without_login(self):
        """Following the redirect shows only the login page, never stock data."""
        from inventory.models import Component

        Component.objects.create(
            component_id="SEC-SECRET-1", name="Hidden Part", price="9.99", quantity=5, minimum_stock=1
        )
        response = self.client.get(reverse("inventory:list"), follow=True)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertNotContains(response, "SEC-SECRET-1")
        self.assertNotContains(response, "Hidden Part")

    def test_login_page_is_reachable(self):
        self.assertEqual(self.client.get(self.login_url).status_code, 200)

    def test_session_cleared_after_logout(self):
        user = get_user_model().objects.create_user(username="sec01", password="Sec@12345")
        self.client.force_login(user)
        self.client.post(reverse("accounts:logout"))
        response = self.client.get(reverse("inventory:list"))
        self.assertEqual(response.status_code, 302)
