"""
Create one demo user per role (for testing and the sprint demo video).

Usage:  python manage.py create_demo_users
"""
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from accounts.roles import ADMIN, MANAGER, STAFF, setup_roles

DEMO_USERS = [
    ("admin1", ADMIN, True),
    ("staff1", STAFF, False),
    ("manager1", MANAGER, False),
]
DEMO_PASSWORD = "Demo@1234"


class Command(BaseCommand):
    help = "Create demo users admin1, staff1 and manager1 (password: Demo@1234)."

    def handle(self, *args, **options):
        setup_roles()
        for username, role, is_staff in DEMO_USERS:
            user, created = User.objects.get_or_create(username=username)
            user.set_password(DEMO_PASSWORD)  # stored hashed (SR-03)
            user.is_staff = is_staff  # admin1 can also open /admin/ for user management
            user.save()
            user.groups.set([Group.objects.get(name=role)])
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} {username} ({role})"))
        self.stdout.write(f"Password for all demo users: {DEMO_PASSWORD}")
