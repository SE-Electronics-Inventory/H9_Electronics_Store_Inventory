"""Make the logged-in user's role available in every template (FR-14)."""
from .roles import ADMIN, get_role


def user_role(request):
    role = get_role(request.user) if hasattr(request, "user") else None
    return {"user_role": role, "is_inventory_admin": role == ADMIN}
