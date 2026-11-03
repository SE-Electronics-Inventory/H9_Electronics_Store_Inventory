"""
Audit Models (FR-16: Implement Inventory Change Tracking, ESIM-F-016 / TC-AUD-01)
"""
from django.conf import settings
from django.db import models


class ChangeLog(models.Model):
    """
    Retains basic information about inventory changes:
    the changed item, action performed, user who did it, and time of change (ESIM-F-016).
    """
    ACTION_CHOICES = [
        ("ADD", "Added"),
        ("EDIT", "Updated"),
        ("DELETE", "Deactivated"),
    ]

    component_id = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name="Component ID",
        help_text="ID of the component at the time of change"
    )
    component_name = models.CharField(
        max_length=200,
        verbose_name="Component Name"
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="Action"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_changes",
        verbose_name="Performed By"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Time of Change"
    )
    details = models.TextField(
        blank=True,
        default="",
        verbose_name="Change Details / Notes"
    )

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Inventory Change Record"
        verbose_name_plural = "Inventory Change Records"

    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.get_action_display()} {self.component_id} by {user_str}"


def log_change(component, action, user=None, details=""):
    """
    Record an inventory change to the audit log (FR-16 / Story #57 / TC-AUD-01).
    Convenience function to create a ChangeLog entry.
    """
    comp_id = getattr(component, "component_id", str(component))
    comp_name = getattr(component, "name", "")
    acting_user = user if (user and user.is_authenticated) else None

    return ChangeLog.objects.create(
        component_id=comp_id,
        component_name=comp_name,
        action=action,
        user=acting_user,
        details=details,
    )
