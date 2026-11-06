"""
SR-06 security test (ESIM-SR-006, TC-SEC-06) – story #47.

Application logs must never contain passwords or secret keys. We capture every
log message written during login, failed login, blocked access and logout,
and check that no secret appears in them.
"""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

PASSWORD = "VerySecret#Pass2026"
WRONG_PASSWORD = "WrongSecret#Guess99"


class CaptureAll(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.lines = []

    def emit(self, record):
        text = self.format(record)
        if record.args:
            text += " " + repr(record.args)
        self.lines.append(text)


class LogSecretTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(username="sec06", password=PASSWORD)
        self.handler = CaptureAll()
        self.root = logging.getLogger()
        self.old_level = self.root.level
        self.root.addHandler(self.handler)
        self.root.setLevel(logging.DEBUG)
        for name in ("django", "django.request", "django.security"):
            logging.getLogger(name).addHandler(self.handler)

    def tearDown(self):
        self.root.removeHandler(self.handler)
        self.root.setLevel(self.old_level)
        for name in ("django", "django.request", "django.security"):
            logging.getLogger(name).removeHandler(self.handler)

    def run_auth_flows(self):
        login = reverse("accounts:login")
        self.client.post(login, {"username": "sec06", "password": WRONG_PASSWORD})  # failed login
        self.client.post(login, {"username": "sec06", "password": PASSWORD})  # good login
        self.client.get(reverse("inventory:add"))  # blocked action (no role) -> logged warning
        self.client.post(reverse("accounts:logout"))  # logout

    def test_logs_contain_no_passwords_or_secret_key(self):
        self.run_auth_flows()
        log_text = "\n".join(self.handler.lines)
        self.assertTrue(self.handler.lines, "expected some log output to inspect")
        for secret in (PASSWORD, WRONG_PASSWORD, settings.SECRET_KEY):
            with self.subTest(secret=secret[:6] + "..."):
                self.assertNotIn(secret, log_text)

    def test_no_custom_logging_of_request_bodies(self):
        """The project must not configure a logger that dumps request data."""
        config = str(getattr(settings, "LOGGING", {}))
        for risky in ("request.POST", "request.body", "password"):
            self.assertNotIn(risky, config)
