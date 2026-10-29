"""
User roles and permissions (FR-14: Role-Based Authorization, ESIM-SR-002).

Each user belongs to one Django group, which is their role:
  - Inventory Administrator: add, edit, delete components and manage users
  - Store Staff:             view and search inventory only
  - Store Manager:           view inventory, dashboard and reports only

The groups are created automatically after `python manage.py migrate`.
Role checks run on the server, so hiding a button is never the only protection.
"""
from functools import wraps

from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.core.exceptions import PermissionDenied

ADMIN = "Inventory Administrator"
STAFF = "Store Staff"
MANAGER = "Store Manager"

ROLE_PERMISSIONS = {
    ADMIN: [
        "inventory.view_component",
        "inventory.add_component",
        "inventory.change_component",
        "inventory.delete_component",
        "auth.view_user",
        "auth.add_user",
        "auth.change_user",
        "auth.delete_user",
    ],
    STAFF: ["inventory.view_component"],
    MANAGER: ["inventory.view_component"],
}

ROLES = list(ROLE_PERMISSIONS)


def setup_roles():
    """Create the three role groups and give each its permissions (safe to run many times)."""
    from django.contrib.auth.models import Group, Permission

    # Make sure permissions exist for every app before assigning them
    for app_config in global_apps.get_app_configs():
        create_permissions(app_config, verbosity=0)

    for role, perm_names in ROLE_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=role)
        perms = []
        for name in perm_names:
            app_label, codename = name.split(".")
            perm = Permission.objects.filter(
                content_type__app_label=app_label, codename=codename
            ).first()
            if perm:
                perms.append(perm)
        group.permissions.set(perms)


def get_role(user):
    """Return the user's role name, or None if they have no role."""
    if not user.is_authenticated:
        return None
    group = user.groups.filter(name__in=ROLES).first()
    return group.name if group else None


def has_role(user, *roles):
    return user.is_authenticated and user.groups.filter(name__in=roles).exists()


def role_required(*roles):
    """View decorator: only users in one of `roles` may continue; others get the Access-denied page (403)."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not has_role(request.user, *roles):
                raise PermissionDenied("Your role is not allowed to perform this action.")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


admin_required = role_required(ADMIN)
