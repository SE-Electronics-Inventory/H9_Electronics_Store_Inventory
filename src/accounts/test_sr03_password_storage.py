"""
SR-03 security test (ESIM-SR-003, TC-SEC-03) – story #43.

Passwords must never be stored as plain text; Django's password hashing is used.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.core.management import call_command
from django.test import TestCase


class PasswordStorageTests(TestCase):
    PLAIN = "PlainText@2026"

    def test_password_is_hashed_not_plain(self):
        user = get_user_model().objects.create_user(username="sec03", password=self.PLAIN)
        user.refresh_from_db()
        self.assertNotEqual(user.password, self.PLAIN)
        self.assertNotIn(self.PLAIN, user.password)
        self.assertTrue(user.check_password(self.PLAIN))

    def test_strong_hasher_is_used(self):
        user = get_user_model().objects.create_user(username="sec03b", password=self.PLAIN)
        hasher = identify_hasher(user.password)
        self.assertIn(hasher.algorithm, {"pbkdf2_sha256", "argon2", "bcrypt_sha256", "scrypt"})

    def test_same_password_gives_different_hashes(self):
        """A random salt is used, so equal passwords do not produce equal hashes."""
        a = get_user_model().objects.create_user(username="sec03c", password=self.PLAIN)
        b = get_user_model().objects.create_user(username="sec03d", password=self.PLAIN)
        self.assertNotEqual(a.password, b.password)

    def test_no_weak_hasher_configured(self):
        hashers = getattr(settings, "PASSWORD_HASHERS", [])
        for weak in ("MD5PasswordHasher", "UnsaltedMD5PasswordHasher", "UnsaltedSHA1PasswordHasher"):
            self.assertFalse(any(weak in h for h in hashers))

    def test_demo_users_are_stored_hashed(self):
        from io import StringIO

        call_command("create_demo_users", stdout=StringIO())
        for user in get_user_model().objects.filter(username__in=["admin1", "staff1", "manager1"]):
            with self.subTest(user=user.username):
                self.assertNotIn("Demo@1234", user.password)
                self.assertTrue(user.check_password("Demo@1234"))
